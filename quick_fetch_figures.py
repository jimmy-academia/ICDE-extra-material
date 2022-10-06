import os
import json
from pathlib import Path
import argparse
import matplotlib.pyplot as plt

def view_plot():
    method_list = ['ia_random', 'ia_popular', 'pga_none', 'srwa_none', 'rev_none', 'trial_none', 'ca_bops', 'mca_msops']
    marker_list = ['P', 'X', 'D', 's', 'P', '^', 'o', '*']
    color_list = ['dimgrey', 'olive', 'teal', 'dodgerblue', 'orange', 'saddlebrown', 'green', 'red']

    parser = argparse.ArgumentParser(description='view_plot')
    parser.add_argument('-p', action='store_true') # do plot
    parser.add_argument('-d', '--d', type=str, default='all') # dataset
    parser.add_argument('-m', '--m', type=str, default='all') # model
    parser.add_argument('--out_dir', type=str, default='figs/quick') 
    parser.add_argument('--num', action='store_true') 
    args = parser.parse_args()

    vmsg = 'plotting' if args.p else 'viewing'
    nmsg = 'opponent number' if args.num else 'opponent capacity'

    args.out_dir = Path(args.out_dir)
    if len(args.d) == 3 and args.d != 'all':
        args.d = {'cia':'ciao', 'epi':'epinions'}[args.d]
    args.dset_list = ['ciao', 'epinions'] if args.d == 'all' else [args.d]
    args.model_list = ['consis'] if args.m == 'all' else [args.m]
    if args.p and not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)

    for dset in args.dset_list:
        print('>>> ', dset)
        for model in args.model_list:
            print('>>> >> >>', model)
            if args.p:
                plt.rcParams["font.family"] = "Times New Roman"
                plt.rcParams["font.size"] = 16
                plt.rcParams["font.weight"] = "bold"
                plt.rcParams["axes.labelweight"] = "bold"
                f, (ax1, ax2) = plt.subplots(1, 2, dpi=300, figsize=(7, 5))
                if args.num:
                    ax1.set_xlabel(r'Number of opponents')
                    ax2.set_xlabel(r'Number of opponents')
                else:
                    ax1.set_xlabel(r"Opponent's budget $\mathregular{b_{op}}$")
                    ax2.set_xlabel(r"Opponent's budget $\mathregular{b_{op}}$")
                ax1.set_ylabel('avg. rate')
                ax2.set_ylabel('HR@3')

            for method, marker, color in zip(method_list, marker_list, color_list):
                avgrate = []
                hrscores = []

                defaultopb = 2
                opt_v = [1,2,3,4] if args.num else [2,3,4,5]
                for opt in range(len(opt_v)):
                    scorefile = 'ckpt/{}p/{}_{}/{}5.json' if args.num else 'ckpt/2p{}/{}_{}/{}5.json'                     
                    v = opt_v[opt] + 1 if args.num else opt_v[opt]
                    v = '' if (not args.num and opt_v[opt]==defaultopb) else v
                    scorefile = scorefile.format(v, dset, method, model)
                    if os.path.exists(scorefile):
                        score = json.load(open(scorefile))
                        avgrate.append(score['avg'])
                        hrscores.append(score['top3'])
                    else:
                        avgrate.append(-1)
                        hrscores.append(-1)
                if args.p:
                    ax1.plot(opt_v, avgrate, marker=marker, color=color)
                    ax2.plot(opt_v, hrscores, marker=marker, color=color)
                else:
                    deci = lambda l: ['\t{:.3f}'.format(x) for x in l]
                    method = '...none' if method == 'none' else method
                    print(method, *deci(avgrate), ' | ', *deci(hrscores))

            type_ = 'num' if args.num else 'cap'
            if args.p:
                thelegend = ['Random', 'Popular', 'PGA', 'S-attack', 'RevAdv', 'Trial', 'BOPDS(CA)', 'MSOPDS']
                # 
                plt.subplots_adjust(top=.7, left=.12, right=.97, bottom=0.15, wspace=0.4)
                f.legend(thelegend, loc='upper center', bbox_to_anchor=(0.5, .97), ncol=4, fancybox=True, prop={'size': 16}, columnspacing=0.25)
                ax1.set_xticks(opt_v, opt_v)
                ax2.set_xticks(opt_v, opt_v)
                f.savefig(args.out_dir/'{}_{}_{}.jpg'.format(dset, model, type_))

    print(vmsg, 'experiment results of', nmsg, opt_v)

if __name__ == '__main__':
    view_plot()
