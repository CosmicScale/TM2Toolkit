# TM2 Toolkit
A toolkit for extracting and creating PlayStation 2 TIM2 textures. Originally developed for use with the PlayStation BB Navigator (PSBBN) textures, but adaptable for other projects too.

## tm2extract.py
Extracts images from PlayStation 2 TIM2 format `.tm2` textures and saves them as `.png` images in the current working directory.

Usage:
```
tm2extract.py [-f|--flatten] <input_file.tm2>
```
- `--flatten` or `-f`: removes the alpha channel in the exported PNG
- Without this flag, the PNG is exported with the alpha channel preserved

## tm2create.py
Creates TIM2 format `.tm2` textures from an image and saves them to the current working directory.

Usage:
```
tm2create.py <input.png>[-f]
```
- Max recommended resolution 256x256
- Some images with very few colors can cause MEDIANCUT to fail, in which case, FASTOCTREE should be used via the -f flag.

## Credits
TM2 Toolkit - Copyright © 2026 by [CosmicScale](https://github.com/CosmicScale)  
All scripts written by [CosmicScale](https://github.com/CosmicScale)