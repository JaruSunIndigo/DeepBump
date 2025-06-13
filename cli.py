import argparse
import numpy as np
import imageio.v3 as iio
import module_color_to_normals
import module_normals_to_curvature
import module_normals_to_height
import module_lowres_to_highres

# Parse CLI args
parser = argparse.ArgumentParser(description="DeepBump CLI")
parser.add_argument("in_img_path", help="path to the input image", type=str)
parser.add_argument("out_img_path", help="path to the output image", type=str)
parser.add_argument(
    "module",
    help="processing to be applied",
    choices=[
        "color_to_normals",
        "normals_to_curvature",
        "normals_to_height",
        "lowres_to_highres",
    ],
)
parser.add_argument(
    "--verbose",
    action=argparse.BooleanOptionalAction,
    help="prints progress to the console",
)
parser.add_argument(
    "--color_to_normals-overlap",
    choices=["SMALL", "MEDIUM", "LARGE"],
    required=False,
    default="LARGE",
)
parser.add_argument(
    "--normals_to_curvature-blur_radius",
    choices=["SMALLEST", "SMALLER", "SMALL", "MEDIUM", "LARGE", "LARGER", "LARGEST"],
    required=False,
    default="MEDIUM",
)
parser.add_argument(
    "--normals_to_height-seamless",
    choices=["TRUE", "FALSE"],
    required=False,
    default="FALSE",
)
parser.add_argument(
    "--lowres_to_highres-scale_factor",
    choices=["x2", "x4"],
    required=False,
    default="FALSE",
)
args = parser.parse_args()


def print_progress(current, total):
    print(f"{current}/{total}")


# Print progress if verbose enabled
if args.verbose:
    progress_callback = print_progress
else:
    progress_callback = None

# Read input image
in_img = iio.imread(args.in_img_path)
# Convert from H,W,C in [0, 256] to C,H,W in [0,1]
in_img = np.transpose(in_img, (2, 0, 1)) / 255

# Apply processing
if args.module == "color_to_normals":
    out_img = module_color_to_normals.apply(
        in_img, args.color_to_normals_overlap, progress_callback
    )
elif args.module == "normals_to_curvature":
    out_img = module_normals_to_curvature.apply(
        in_img, args.normals_to_curvature_blur_radius, progress_callback
    )
elif args.module == "normals_to_height":
    out_img = module_normals_to_height.apply(
        in_img, args.normals_to_height_seamless == "TRUE", progress_callback
    )
elif args.module == "lowres_to_highres":
    out_img = module_lowres_to_highres.apply(
        in_img, args.lowres_to_highres_scale_factor, progress_callback
    )

# Convert from C,H,W in [0,1] to H,W,C in [0, 256]
out_img = (np.transpose(out_img, (1, 2, 0)) * 255).astype(np.uint8)
# Write output image
iio.imwrite(args.out_img_path, out_img)
