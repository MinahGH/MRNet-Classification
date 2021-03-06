# -*- coding: utf-8 -*-
"""Assignment4PR.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1A4eHaXnuesZjvs3HS61c19jqO4f6CxQo
"""

from google.colab import drive
drive.mount('/content/gdrive')
root_path = 'gdrive/My Drive/'
import numpy as np
import os
import pandas as pd
import io
from google.colab import files
import matplotlib.pyplot as plt
from urllib.request import urlopen,urlretrieve
from PIL import Image
from tqdm import tqdm_notebook
# %matplotlib inline
from sklearn.utils import shuffle
import cv2
#from resnets_utils import *
from sklearn.model_selection import train_test_split
from keras.models import load_model
from sklearn.datasets import load_files   
from keras.utils import np_utils
from glob import glob
from keras import applications
from keras.preprocessing.image import ImageDataGenerator 
from keras import optimizers
from keras.models import Sequential,Model,load_model
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D,GlobalAveragePooling2D
from keras.callbacks import TensorBoard,ReduceLROnPlateau,ModelCheckpoint
import random

#uploaded = os.chdir()
path ='/content/gdrive/My Drive/MR_data/MRNet-v1.0/' #change dir

#uploaded = files.upload()


abnormal =np.asarray( pd.read_csv(path+'train-abnormal.csv',header=None) )
abnormal_test =np.asarray( pd.read_csv(path+'valid-abnormal.csv',header=None) )
acl =np.asarray( pd.read_csv(path+'train-acl.csv',header=None))
acl_test =np.asarray( pd.read_csv(path+'valid-acl.csv',header=None) )
meniscus = np.asarray(pd.read_csv(path+'train-meniscus.csv',header=None))
meniscus_test =np.asarray( pd.read_csv(path+'valid-meniscus.csv',header=None) )
labels = pd.DataFrame({'abnormal' : abnormal[:,1],'acl' : acl[:,1],'meniscus' : meniscus[:,1]})
labels_test = pd.DataFrame({'abnormal' : abnormal_test[:,1],'acl' : acl_test[:,1],'meniscus' : meniscus_test[:,1]})

dim = (256,256)
AbnormalLabels=[]
AclLabels=[]
MeniscusLabels=[]

def Squeeze(myarr,mini):
  s=0
  labels=[]
  end=len(myarr)/mini
  j=0
  while(j!=end):
    sa = myarr[s:(s+mini)]
    s=s+mini
    count=0
    for i in sa:
      if i == 1:
        count+=1
        
    if count >(mini/2) :
      labels.append(1)
    else:  
      labels.append(0)  
    j=j+1  
  return labels 


def read_data(file):
  
  sizes=[]
  vec=[]
  last=[]
  for filename in sorted(os.listdir(path+file)):
      #print(path+file+'/'+filename)
      data = np.load(path+file+'/'+filename)
      sizes.append(data.shape[0])
      vec.append(data)
  sizes =sizes[:int(len(sizes)/2)]
  vec =vec[:int(len(vec)/2)] 
  
  min_slices = min(sizes)
  for x in vec :
     temp = np.array(random.choices(x,k=min_slices))
     for y in temp :
        img = cv2.resize(y, dim, interpolation = cv2.INTER_AREA)
        img_rgb = np.asarray(np.dstack((img, img, img)), dtype=np.uint8)
        last.append(img_rgb)
  return last,min_slices
            
def ext_labels(sizes,dis):  
  disLabels=[]
  for i in range (int(len(dis)/2)):
    for j in range (0,sizes):
      disLabels.append(dis[i])
  return disLabels 

last=0
img_height,img_width = 256,256 
num_classes = 2



from sklearn.metrics import f1_score


def CallModel(mytrain,mytest):
  
  base_model = applications.resnet50.ResNet50(weights= 'imagenet', include_top=False, input_shape= (img_height,img_width,3))
  x = base_model.output
  x = MaxPool2D()(x)
  x = Dropout(0.7)(x)
  x = GlobalAveragePooling2D()(x)
  x = Dropout(0.7)(x)
 
  predictions = Dense(num_classes, activation= 'softmax')(x)
  model = Model(inputs = base_model.input, outputs = predictions)
  from keras.optimizers import SGD, Adam
  adam = Adam(lr=0.0001)
  model.compile(optimizer= adam, loss='categorical_crossentropy', metrics=['accuracy'])
  print('print fit 0')
  #print(min_slices_test)
  #print(len(Squeeze(AbnormalLabelsTest[:,1],min_slices_test)))
  history=model.fit(mytrain, AbnormalLabels, epochs = 7, batch_size = min_slices_train)
  print('print eval 0')
  preds0 = model.evaluate(mytest, AbnormalLabelsTest, batch_size = 64)
  preds00 = model.predict(mytest) 
  plotty0abnormal = preds00.argmax(axis=-1) #predictions
  plotty0=Squeeze(plotty0abnormal,min_slices_test)
  #print(AbLT)
  #print(len(AbLT))
  #print(plotty0)
  #print(len(plotty0))
  result=f1_score(AbLT[:int(len(AbLT)/2)], plotty0, average=None)
  #result=f1_score(AbnormalLabelsTest, plotty0, average=None)
  print('F-Scores for Axial/Coronal/Sagittal-Abnormal: ')
  print(result)
  plt.title('Accuracy')
  plt.plot(history.history['acc'], label='train')
  plt.legend()
  plt.show()
  #model.summary()
  
  print('print fit 1')
  p1=model.fit(mytrain, AclLabels, epochs = 3, batch_size = min_slices_train)
  print('print eval 1')
  preds1 = model.evaluate(mytest, AclLabelsTest, batch_size = 64)
  preds11 = model.predict(mytest) 
  plotty1Acl = preds11.argmax(axis=-1) #predictions
  plotty1=Squeeze(plotty1Acl,min_slices_test)  
  result=f1_score(AcLT[:int(len(AcLT)/2)], plotty1, average=None)  
  #result=f1_score(AcLT, plotty1, average=None)
  print('F-Scores for Axial/Coronal/Sagittal-ACL: ')
  print(result)
  plt.title('Accuracy')
  plt.plot(p1.history['acc'], label='train')
  plt.legend()
  plt.show()
  #model.summary()
  
  print('printfit 2')
  p2=model.fit(mytrain, MeniscusLabels, epochs = 3, batch_size = min_slices_train)
  print('print eval 2')
  preds2 = model.evaluate(mytest, MeniscusLabelsTest, batch_size = 64)
  preds22 = model.predict(mytest) 
  plotty2Menis = preds22.argmax(axis=-1) #predictions
  plotty2=Squeeze(plotty2Menis,min_slices_test)
  
  result=f1_score(MeLT[:int(len(MeLT)/2)], plotty2, average=None)
  #result=f1_score(MeLT, plotty2, average=None)
  print('F-Scores for Axial/Coronal/Sagittal-Meniscus: ')
  print(result)
  plt.title('Accuracy')
  plt.plot(p2.history['acc'], label='train')
  plt.legend()
  plt.show()
  #model.summary()

  print ("Loss = " + str(preds0[0]))
  print ("Test Accuracy = " + str(preds0[1]))
  print ("Loss = " + str(preds1[0]))
  print ("Test Accuracy = " + str(preds1[1]))
  print ("Loss = " + str(preds2[0]))
  print ("Test Accuracy = " + str(preds2[1]))

  return plotty0abnormal,plotty1Acl,plotty2Menis


axial_train,min_slices_train = read_data('train/axial')
axial_train= np.asarray(axial_train)
print(axial_train.shape)
AbnormalLabels = np.asarray(ext_labels(min_slices_train,labels['abnormal' ]) )
AclLabels = np.asarray(ext_labels(min_slices_train,labels['acl' ]) ) 
MeniscusLabels = np.asarray(ext_labels(min_slices_train,labels['meniscus' ]) )
AbnormalLabels = np.vstack((AbnormalLabels,AbnormalLabels)).T
AclLabels = np.vstack((AclLabels,AclLabels)).T
MeniscusLabels = np.vstack((MeniscusLabels,MeniscusLabels)).T
axial_test , min_slices_test = read_data ('valid/axial') 
axial_test =np.asarray(axial_test)

AbLT=np.asarray(labels_test['abnormal'])
AbnormalLabelsTest = np.asarray(ext_labels(min_slices_test,labels_test['abnormal']))
print(len(AbnormalLabelsTest))
AcLT=np.asarray(labels_test['acl'])
AclLabelsTest = np.asarray(ext_labels(min_slices_test,labels_test['acl']))
MeLT=np.asarray(labels_test['meniscus'])
MeniscusLabelsTest = np.asarray(ext_labels(min_slices_test,labels_test['meniscus']))
AbnormalLabelsTest = np.vstack((AbnormalLabelsTest,AbnormalLabelsTest)).T
AclLabelsTest= np.vstack((AclLabelsTest,AclLabelsTest)).T
MeniscusLabelsTest = np.vstack((MeniscusLabelsTest,MeniscusLabelsTest)).T 
print('printing all 3 shapes..')

print(AbnormalLabels.shape)
print(AclLabels.shape)
print(MeniscusLabels.shape)
abnormalAxial,aclAxial,MeniscusAxial= CallModel(axial_train,axial_test)                  #####################################axial
print('5alast run el AXIAL')


coronal_train,min_slices_train = read_data('train/coronal')
coronal_train= np.asarray(coronal_train)
AbnormalLabels = np.asarray(ext_labels(min_slices_train,labels['abnormal' ]) )
AclLabels = np.asarray(ext_labels(min_slices_train,labels['acl' ]) ) 
MeniscusLabels = np.asarray(ext_labels(min_slices_train,labels['meniscus' ]) )
AbnormalLabels = np.vstack((AbnormalLabels,AbnormalLabels)).T
AclLabels = np.vstack((AclLabels,AclLabels)).T
MeniscusLabels = np.vstack((MeniscusLabels,MeniscusLabels)).T





print('printing all 3 shapes..')

print(AbnormalLabels.shape)
print(AclLabels.shape)
print(MeniscusLabels.shape)
print(coronal_train.shape)
coronal_test , min_slices_test = read_data ('valid/coronal') 
coronal_test =np.asarray(coronal_test)
AbLT=np.asarray(labels_test['abnormal'])
AbnormalLabelsTest = np.asarray(ext_labels(min_slices_test,labels_test['abnormal']))
AcLT=np.asarray(labels_test['acl'])
AclLabelsTest = np.asarray(ext_labels(min_slices_test,labels_test['acl']))
MeLT=np.asarray(labels_test['meniscus'])
MeniscusLabelsTest = np.asarray(ext_labels(min_slices_test,labels_test['meniscus']))
AbnormalLabelsTest = np.vstack((AbnormalLabelsTest,AbnormalLabelsTest)).T
AclLabelsTest= np.vstack((AclLabelsTest,AclLabelsTest)).T
MeniscusLabelsTest = np.vstack((MeniscusLabelsTest,MeniscusLabelsTest)).T 
abnormalCoronal,aclCoronal,MeniscusCoronal=CallModel(coronal_train,coronal_test)  #####################################coronal
#CallModel(coronal_train,coronal_test)
print('5alast run el CORONAL')

sagittal_train,min_slices_train = read_data('train/sagittal')
sagittal_train= np.asarray(sagittal_train)
AbnormalLabels = np.asarray(ext_labels(min_slices_train,labels['abnormal' ]) )
AclLabels = np.asarray(ext_labels(min_slices_train,labels['acl' ]) ) 
MeniscusLabels = np.asarray(ext_labels(min_slices_train,labels['meniscus' ]) )
AbnormalLabels = np.vstack((AbnormalLabels,AbnormalLabels)).T
AclLabels = np.vstack((AclLabels,AclLabels)).T
MeniscusLabels = np.vstack((MeniscusLabels,MeniscusLabels)).T
print('printing all 3 shapes..')

print(AbnormalLabels.shape)
print(AclLabels.shape)
print(MeniscusLabels.shape)
print(sagittal_train.shape)
sagittal_test , min_slices_test= read_data ('valid/sagittal') 
sagittal_test =np.asarray(sagittal_test)
AbLT=np.asarray(labels_test['abnormal'])
AbnormalLabelsTest = np.asarray(ext_labels(min_slices_test,labels_test['abnormal']))
AcLT=np.asarray(labels_test['acl'])
AclLabelsTest = np.asarray(ext_labels(min_slices_test,labels_test['acl']))
MeLT=np.asarray(labels_test['meniscus'])
MeniscusLabelsTest = np.asarray(ext_labels(min_slices_test,labels_test['meniscus']))
AbnormalLabelsTest = np.vstack((AbnormalLabelsTest,AbnormalLabelsTest)).T
AclLabelsTest= np.vstack((AclLabelsTest,AclLabelsTest)).T
MeniscusLabelsTest = np.vstack((MeniscusLabelsTest,MeniscusLabelsTest)).T 
abnormalSagittal,aclSagittal,MeniscuSagittal=CallModel(sagittal_train,sagittal_test)   #####################################sagittal
#CallModel(sagittal_train,sagittal_test)
print('5alast run el SAGITTAL')



def function1 (ArrayOfAccuracies):
  avg=[]
  flagArray=[]
  for i in range (0,len(ArrayOfAccuracies),3):
    temp=[]
    temp.append(ArrayOfAccuracies[i])
    temp.append(ArrayOfAccuracies[i+1])
    temp.append(ArrayOfAccuracies[i+2])
    avg.append((temp[0]+temp[1]+temp[2])/3)
    flag = 1 #sick
    sum=0
    for x in temp: 
      if (x < 0.5):
        sum=sum+1  # number of accuracies below 0.5     
    if(sum > 1):
      flag = 0 # healthy  
    flagArray.append(flag)  
  return flagArray,avg 



def function2 (ArrayOfLabels):
  flagArray=[]
  for i in range (0,len(ArrayOfLabels),3):
    temp=[]
    temp.append(ArrayOfLabels[i])
    temp.append(ArrayOfLabels[i+1])
    temp.append(ArrayOfLabels[i+2])
    flag = 1 #sick
    sum=0
    for x in temp: 
      if (x == 0):
        sum=sum+1  # number of labels equal 0  (healthy)   
    if(sum > 1):
      flag = 0 # healthy
    flagArray.append(flag)
  return flagArray

abL=[]
aclL=[]
mL=[]

print("length abnormalaxial")
print(len(abnormalAxial))
print("length abnormalCoronal")
print(len(abnormalCoronal))
print("length abnormalSagittal")
print(len(abnormalSagittal))

for i in range (0, len(abnormalCoronal)):
  abL.append(abnormalAxial[i])
  abL.append(abnormalCoronal[i])
  abL.append(abnormalSagittal[i])
  
l1=function2(abL) 
print("first label")
print(len(l1))
print(l1)

for i in range (0, len(aclCoronal)):
  aclL.append(aclCoronal[i])
  aclL.append(aclAxial[i])
  aclL.append(aclSagittal[i])
  
l2=function2(aclL)  
print("second label")
print(len(l2))
print(l2)  
  
for i in range (0, len(MeniscusCoronal)):
  mL.append(MeniscusCoronal[i])
  mL.append(MeniscusAxial[i])
  mL.append(MeniscuSagittal[i])
  
l3=function2(mL)
print("third label")
print(len(l3))
print(l3)