# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 10:52:16 2019
@author: ZeyuGao

This mudole is for cancer region detection (2 class) and subtype (3 class)
Trained with ResNet34
cancer region detection: 0 cancer 1 normal
subtype: 0 ccrcc 1 prcc 2 chrcc
iuput image size must be 2000 * 2000
data_array size is (x, 2000, 2000, 3) RGB
"""

#### ccrcc cancer region detection #####
import math
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim
import torch.utils.data
import torchvision.transforms as transforms
import torch.utils.data as data
from PIL import Image
from tqdm import tqdm
import numpy as np
from Controller import resynet


# os.environ['CUDA_VISIBLE_DEVICES'] = '5'
# file_path_base = "../model/resnet_34_crd_model_59.pth"

def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def softmax(x):
    return np.exp(x) / sum(np.exp(x))


class CancerDataset(data.Dataset):

    def __init__(self, data, labels, transform=None):
        self.data = data
        self.labels = labels
        self.transform = transform

    def __getitem__(self, index):
        img, target = self.data[index], self.labels[index]
        img = Image.fromarray(img)
        if self.transform is not None:
            img = self.transform(img)
        return img, target

    def __len__(self):
        return len(self.labels)


class ResNetClassification(object):

    def __init__(self, model_path, batch_size=64, num_workers=0):
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.base_model = self._load_model(model_path)

        normMean = [0.744, 0.544, 0.670]
        normStd = [0.183, 0.245, 0.190]
        normTransform = transforms.Normalize(normMean, normStd)
        self.test_transform = transforms.Compose([
            transforms.Resize(224),
            transforms.ToTensor(),
            normTransform
        ])

    def _load_dataset(self, data_array, labels):
        test_data = CancerDataset(data_array, labels, transform=self.test_transform)
        test_loader = torch.utils.data.DataLoader(
            test_data, batch_size=self.batch_size, shuffle=False,
            num_workers=self.num_workers, pin_memory=False)
        return test_loader

    def _load_model(self, model_path):
        base_model = resynet.resnet34(pretrained=True, num_classes_1=2, num_classes_2=3)
        base_model = base_model.cuda()
        base_model = torch.nn.DataParallel(base_model)
        checkpoint = torch.load(model_path)
        try:
            base_model.load_state_dict(checkpoint['state_dict'])
        except:
            base_model.load_state_dict(checkpoint['net'])
        return base_model

    def predict(self, data_array):
        labels = list(-1 for i in range(data_array.shape[0]))
        test_loader = self._load_dataset(data_array, labels)
        cudnn.benchmark = True
        outputs_all1 = []
        outputs_all2 = []
        self.base_model.eval()
        with torch.no_grad():
            for batch_idx, (inputs, targets) in enumerate(test_loader):
                inputs, targets = inputs.to('cuda'), targets.type(torch.LongTensor).to('cuda')
                outputs1, outputs2 = self.base_model(inputs)
                if outputs_all1 == []:
                    outputs_all1 = outputs1.cpu().data.numpy()
                else:
                    outputs_all1 = np.concatenate((outputs_all1, outputs1.cpu().data.numpy()), axis=0)
                if outputs_all2 == []:
                    outputs_all2 = outputs2.cpu().data.numpy()
                else:
                    outputs_all2 = np.concatenate((outputs_all2, outputs1.cpu().data.numpy()), axis=0)
            outputs_all1 = [softmax(outputs_all1[i])
                            for i in range(outputs_all1.shape[0])]
            outputs_all2 = [softmax(outputs_all2[i])
                            for i in range(outputs_all2.shape[0])]
        return np.array(outputs_all1), np.array(outputs_all2)
