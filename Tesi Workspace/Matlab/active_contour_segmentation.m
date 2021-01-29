%Active contours

rootdir = '/home/markosan/Matlab/test';
filelist = dir(fullfile(rootdir, '**/*mm.png')); 
for k = 1:numel(filelist)
    F = string(filelist(k).folder)+"/"+ string(filelist(k).name);
    I = imread(F);
    if length(size(I)) > 2 
        I = rgb2gray(I);
    end
    imshow(I,'InitialMagnification','fit')
    mask = zeros(size(I));
    mask(5:end-5,5:end-5) = 1;
    bw = activecontour(I,mask,100);
    bw = bwareafilt(bw,1);
    title('Active contour')
    boundary = bw - imerode(bw,[0 1 0; 1 1 1; 0 1 0]);
    boundary = uint8(boundary*255);
    output = I(:,:,[1 1 1]);
    output(:,:,1) = output(:,:,1) + boundary;
    output(:,:,2) = output(:,:,2) - boundary;
    output(:,:,3) = output(:,:,3) - boundary;
    imshow(output);
    sname = ("/home/markosan/Matlab/results/"+erase(F,"/home/markosan/Matlab/")+"_segmented.png")
    bname = ("/home/markosan/Matlab/results/"+erase(F,"/home/markosan/Matlab/")+"_border.png")
    pause(30)
    %imwrite(output, bname);
    %imwrite(bw, sname);
end





