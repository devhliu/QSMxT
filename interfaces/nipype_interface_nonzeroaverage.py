#!/usr/bin/env python3

from nipype.interfaces.base import SimpleInterface, BaseInterfaceInputSpec, TraitedSpec, InputMultiPath, File


def nonzero_average(in_files, mask_files=None, save_result=True):
    import os
    import nibabel as nib
    import numpy as np

    if len(in_files) == 1: return in_files[0]

    data = []
    for in_data_file in in_files:
        in_data_nii = nib.load(in_data_file)
        in_data = in_data_nii.get_fdata()
        data.append(in_data)
    data = np.array(data)

    if mask_files:
        mask = []
        for in_mask_file in mask_files:
            in_mask_nii = nib.load(in_mask_file)
            in_data = in_mask_nii.get_fdata()
            mask.append(in_data)
        mask = np.array(mask, dtype=int)
        mask *= abs(data) >= 5e-5
    else:
        mask = abs(data) >= 5e-5
    
    try:
        final = data.sum(0) / mask.sum(0)
    except ValueError:
        raise ValueError(f"Tried to average files of incompatible dimensions; data.shape[..]={[x.shape for x in data]}")

    if save_result:
        filename = f"{os.path.abspath(os.path.split(in_files[0])[1].split('.')[0])}_average.nii"
        nib.save(nib.nifti1.Nifti1Image(final, affine=in_data_nii.affine, header=in_data_nii.header), filename)
        return filename

    return final


class NonzeroAverageInputSpec(BaseInterfaceInputSpec):
    in_files = InputMultiPath(mandatory=True, exists=True)
    in_masks = InputMultiPath(mandatory=False, exists=True)


class NonzeroAverageOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class NonzeroAverageInterface(SimpleInterface):
    input_spec = NonzeroAverageInputSpec
    output_spec = NonzeroAverageOutputSpec

    def _run_interface(self, runtime):
        self._results['out_file'] = nonzero_average(self.inputs.in_files, self.inputs.in_masks)
        return runtime


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'in_files',
        nargs='+',
        type=str
    )

    parser.add_argument(
        'in_masks',
        nargs='*',
        type=str
    )

    parser.add_argument(
        'out_file',
        type=str
    )

    args = parser.parse_args()
    qsm_final = nonzero_average(args.in_files, args.in_masks, True);

