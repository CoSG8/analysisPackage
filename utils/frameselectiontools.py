"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut
Please see AUTHORS for contributors.

https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0
"""

import numpy as np
from skimage.util import img_as_ubyte
from sklearn.cluster import MiniBatchKMeans
import cv2
from tqdm import tqdm

def KmeansbasedFrameselectioncv2(cap,numframes2pick,start,stop,crop,coords,Index=None,step=1,resizewidth=30,batchsize=100,max_iter=50,color=False):
    nframes=cap.get(7)
    ny=int(cap.get(4))
    nx=int(cap.get(3))
    ratio=resizewidth*1./nx
    if ratio>1:
         raise Exception("Choise of resizewidth actually upsamples!")

    print("Kmeans-quantization based extracting of frames from",  round(start*nframes*1./cap.get(5),2)," seconds to", round(stop*nframes*1./cap.get(5),2), " seconds.")
    startindex=int(np.floor(nframes*start))
    stopindex=int(np.ceil(nframes*stop))

    if Index is None:
        Index=np.arange(startindex,stopindex,step)
    else:
        Index=np.array(Index)
        Index=Index[(Index>startindex)*(Index<stopindex)] #crop to range!

    nframes=len(Index)
    if batchsize>nframes:
        batchsize=int(nframes/2)

    allocated=False
    if len(Index)>=numframes2pick:
        if np.mean(np.diff(Index))>1: #then non-consecutive indices are present, thus cap.set is required (which slows everything down!)
            print("Extracting and downsampling...",nframes, " frames from the video.")
            if color:
                for counter,index in tqdm(enumerate(Index)):
                    cap.set(1,index) #extract a particular frame
                    ret, frame = cap.read()
                    if ret:
                        if crop:
                            frame=frame[int(coords[2]):int(coords[3]),int(coords[0]):int(coords[1]),:]

                        #image=img_as_ubyte(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),None,fx=ratio,fy=ratio))
                        image=img_as_ubyte(cv2.resize(frame,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_NEAREST)) #color trafo not necessary; lack thereof improves speed.
                        if not allocated: #'DATA' not in locals(): #allocate memory in first pass
                            DATA=np.empty((nframes,np.shape(image)[0],np.shape(image)[1]*3))
                            allocated=True
                        DATA[counter,:,:] = np.hstack([image[:,:,0],image[:,:,1],image[:,:,2]])
            else:
                for counter,index in tqdm(enumerate(Index)):
                    cap.set(1,index) #extract a particular frame
                    ret, frame = cap.read()
                    if ret:
                        if crop:
                            frame=frame[int(coords[2]):int(coords[3]),int(coords[0]):int(coords[1]),:]
                        #image=img_as_ubyte(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),None,fx=ratio,fy=ratio))
                        image=img_as_ubyte(cv2.resize(frame,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_NEAREST)) #color trafo not necessary; lack thereof improves speed.
                        if not allocated: #'DATA' not in locals(): #allocate memory in first pass
                            DATA=np.empty((nframes,np.shape(image)[0],np.shape(image)[1]))
                            allocated=True
                        DATA[counter,:,:] = np.mean(image,2)
        else:
            print("Extracting and downsampling...",nframes, " frames from the video.")
            if color:
                for counter,index in tqdm(enumerate(Index)):
                    ret, frame = cap.read()
                    if ret:
                        if crop:
                            frame=frame[int(coords[2]):int(coords[3]),int(coords[0]):int(coords[1]),:]

                        #image=img_as_ubyte(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),None,fx=ratio,fy=ratio))
                        image=img_as_ubyte(cv2.resize(frame,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_NEAREST)) #color trafo not necessary; lack thereof improves speed.
                        if not allocated: #'DATA' not in locals(): #allocate memory in first pass
                            DATA=np.empty((nframes,np.shape(image)[0],np.shape(image)[1]*3))
                            allocated=True
                        DATA[counter,:,:] = np.hstack([image[:,:,0],image[:,:,1],image[:,:,2]])
            else:
                for counter,index in tqdm(enumerate(Index)):
                    ret, frame = cap.read()
                    if ret:
                        if crop:
                            frame=frame[int(coords[2]):int(coords[3]),int(coords[0]):int(coords[1]),:]
                        #image=img_as_ubyte(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),None,fx=ratio,fy=ratio))
                        image=img_as_ubyte(cv2.resize(frame,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_NEAREST)) #color trafo not necessary; lack thereof improves speed.
                        if not allocated: #'DATA' not in locals(): #allocate memory in first pass
                            DATA=np.empty((nframes,np.shape(image)[0],np.shape(image)[1]))
                            allocated=True
                        DATA[counter,:,:] = np.mean(image,2)

        print("Kmeans clustering ... (this might take a while)")
        data = DATA - DATA.mean(axis=0)
        data=data.reshape(nframes,-1) #stacking

        kmeans=MiniBatchKMeans(n_clusters=numframes2pick, tol=1e-3, batch_size=batchsize,max_iter=max_iter)
        kmeans.fit(data)
        frames2pick=[]
        for clusterid in range(numframes2pick): #pick one frame per cluster
            clusterids=np.where(clusterid==kmeans.labels_)[0]

            numimagesofcluster=len(clusterids)
            if numimagesofcluster>0:
                frames2pick.append(Index[clusterids[np.random.randint(numimagesofcluster)]])
        #cap.release() >> still used in frame_extraction!
        return list(np.array(frames2pick))
    else:
        return list(Index)
