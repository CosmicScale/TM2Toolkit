# TM2 Toolkit
A toolkit for extracting and creating PlayStation 2 TIM2 textures. Originally developed for use with the PlayStation BB Navigator (PSBBN) textures, but adaptable for other projects too.

## tm2extract.py
Extracts images from PlayStation 2 TIM2 format `.tm2` textures and saves them as `.png` images in the current working directory.

Usage:
```
tm2extract.py [-a|--alpha] <input_file.tm2>
```
- `--alpha` or `-a`: preserves the alpha channel in the exported PNG
- Without this flag, the PNG is exported without an alpha channel

## psm2tm2.py
Extracts PlayStation 2 TIM2 format `.tm2` textures from PS2S format `.psm` video containers and saves them to the current working directory.

Usage:
```
psm2tm2.py <input_file.psm>
```

## tm2create.py
Creates TIM2 format `.tm2` textures from an image and saves them to the current working directory. Max resolution 256x256.

Usage:
```
tm2create.py <input.png>
```

## Credits
TM2 Toolkit - Copyright © 2026 by [CosmicScale](https://github.com/CosmicScale)  
All scripts written by [CosmicScale](https://github.com/CosmicScale)