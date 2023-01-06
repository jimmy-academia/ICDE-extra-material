# python tech/process_pga.py

import torch
import numpy as np
def main():
    result = []
    for dset in ['epi', 'ciao']:
        file_path = '../pga/save_{}.npy'.format(dset)
        out_path = 'cbase/pga_{}.pt'.format(dset[:3])
        print('loaded', file_path)
        fake_ratings = np.load(file_path)
        fake_ratings = torch.from_numpy(fake_ratings)
        ind = torch.sort(fake_ratings.abs(), descending=True)[1][:, :100]
        for fu, fu_iids in enumerate(ind):
            for iid in fu_iids:
                r = fake_ratings[fu, iid]
                r = max(-1, min(r, 1))
                result.append([fu,  int(iid), int(2* (r+1)+1)])
        torch.save(result, out_path)
        print('saved', out_path)
if __name__ == '__main__':
    main()