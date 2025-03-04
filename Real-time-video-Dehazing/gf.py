import numpy as np
import scipy as sp
import scipy.ndimage


def box(img, r):
    """ O(1) box filter
        img - >= 2d image
        r   - radius of box filter
    """
    (rows, cols) = img.shape[:2]
    imDst = np.zeros_like(img)

    tile = [1] * img.ndim
    tile[0] = r
    imCum = np.cumsum(img, 0)
    imDst[0:r+1, :, ...] = imCum[r:2*r+1, :, ...]
    imDst[r+1:rows-r, :, ...] = imCum[2*r+1:rows, :, ...] - imCum[0:rows-2*r-1, :, ...]
    imDst[rows-r:rows, :, ...] = np.tile(imCum[rows-1:rows, :, ...], tile) - imCum[rows-2*r-1:rows-r-1, :, ...]

    tile = [1] * img.ndim
    tile[1] = r
    imCum = np.cumsum(imDst, 1)
    imDst[:, 0:r+1, ...] = imCum[:, r:2*r+1, ...]
    imDst[:, r+1:cols-r, ...] = imCum[:, 2*r+1:cols, ...] - imCum[:, 0:cols-2*r-1, ...]
    imDst[:, cols-r:cols, ...] = np.tile(imCum[:, cols-1:cols, ...], tile) - imCum[:, cols-2*r-1:cols-r-1, ...]

    return imDst

import numpy as np
import scipy as sp
import cv2

def box(I, r):
    """ Box filter (simple moving average) """
    return cv2.boxFilter(I, -1, (r, r))

def guided_filter(I, p, r, eps, s=None):
    """ Guided filter per channel
        I - guide image (1 or 3 channels)
        p - filtering input (1 or n channels)
        r - window radius
        eps - regularization (roughly, variance of non-edge noise)
        s - subsampling factor for fast guided filter
    """
    if p.ndim == 2:
        p = p[..., np.newaxis]  # If p is grayscale, add an extra dimension

    out = np.zeros_like(p)
    
    # Apply the guided filter for each channel
    for ch in range(p.shape[2]):
        out[..., ch] = _gf_color(I, p[..., ch], r, eps, s)

    return np.squeeze(out) if p.ndim == 2 else out

def _gf_color(I, p, r, eps, s=None):
    """ Color guided filter """
    if s is not None:
        # Subsample the images and reduce radius accordingly
        I = sp.ndimage.zoom(I, [1/s, 1/s, 1], order=1)
        p = sp.ndimage.zoom(p, [1/s, 1/s], order=1)
        r = round(r / s)

    h, w = p.shape[:2]
    N = box(np.ones((h, w)), r)

    # Compute the mean for each color channel (R, G, B) and the input image
    mI_r = box(I[:, :, 0], r) / N
    mI_g = box(I[:, :, 1], r) / N
    mI_b = box(I[:, :, 2], r) / N
    mP = box(p, r) / N

    # Compute the mean of the product of the input image and guidance image
    mIp_r = box(I[:, :, 0] * p, r) / N
    mIp_g = box(I[:, :, 1] * p, r) / N
    mIp_b = box(I[:, :, 2] * p, r) / N

    # Covariance between input and guidance image
    covIp_r = mIp_r - mI_r * mP
    covIp_g = mIp_g - mI_g * mP
    covIp_b = mIp_b - mI_b * mP

    # Variance of the guidance image channels
    var_I_rr = box(I[:, :, 0] * I[:, :, 0], r) / N - mI_r * mI_r
    var_I_rg = box(I[:, :, 0] * I[:, :, 1], r) / N - mI_r * mI_g
    var_I_rb = box(I[:, :, 0] * I[:, :, 2], r) / N - mI_r * mI_b
    var_I_gg = box(I[:, :, 1] * I[:, :, 1], r) / N - mI_g * mI_g
    var_I_gb = box(I[:, :, 1] * I[:, :, 2], r) / N - mI_g * mI_b
    var_I_bb = box(I[:, :, 2] * I[:, :, 2], r) / N - mI_b * mI_b

    a = np.zeros((h, w, 3))
    
    # Solve for 'a' using the covariance and variance of the guidance image
    for i in range(h):
        for j in range(w):
            sig = np.array([
                [var_I_rr[i, j], var_I_rg[i, j], var_I_rb[i, j]],
                [var_I_rg[i, j], var_I_gg[i, j], var_I_gb[i, j]],
                [var_I_rb[i, j], var_I_gb[i, j], var_I_bb[i, j]]
            ])
            covIp = np.array([covIp_r[i, j], covIp_g[i, j], covIp_b[i, j]])
            a[i, j, :] = np.linalg.solve(sig + eps * np.eye(3), covIp)

    # Compute b (bias term) for each pixel
    b = mP - a[:, :, 0] * mI_r - a[:, :, 1] * mI_g - a[:, :, 2] * mI_b

    # Compute the means of a and b
    meanA = box(a, r) / N[..., np.newaxis]
    meanB = box(b, r) / N

    if s is not None:
        # Rescale back the means after subsampling
        meanA = sp.ndimage.zoom(meanA, [s, s, 1], order=1)
        meanB = sp.ndimage.zoom(meanB, [s, s], order=1)

    # Final output calculation
    q = np.sum(meanA * I, axis=2) + meanB

    return q


def _gf_gray(I, p, r, eps, s=None):
    """ Grayscale guided filter """
    if s is not None:
        Isub = sp.ndimage.zoom(I, 1/s, order=1)
        Psub = sp.ndimage.zoom(p, 1/s, order=1)
        r = round(r / s)
    else:
        Isub = I
        Psub = p

    (rows, cols) = Isub.shape
    N = box(np.ones([rows, cols]), r)

    meanI = box(Isub, r) / N
    meanP = box(Psub, r) / N
    corrI = box(Isub * Isub, r) / N
    corrIp = box(Isub * Psub, r) / N

    covIp = corrIp - meanI * meanP
    varI = corrI - meanI * meanI
    a = covIp / (varI + eps)
    b = meanP - a * meanI

    meanA = box(a, r) / N
    meanB = box(b, r) / N
    q = meanA * Isub + meanB
    return q
