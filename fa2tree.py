#!/usr/bin/env python3

import os, subprocess, click, sys
from Bio import SeqIO
from glob import glob
import pandas as pd


HOME = os.getenv('HOME')

def runCMD(cmd):
    print(cmd)
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        _out,_err = proc.communicate()
    if _err:
        sys.exit(_err.decode('utf-8'))
    print(_out.decode('utf-8'))


def std_infile(input,std_file):

    std_fasta = []
    
    for _ in SeqIO.parse(input,'fasta'):
    
        if ':' in _.id:
            _.id = _.id.replace(':','_')
            _.description = ''
            std_fasta.append(_)
    
        else:
            std_fasta.append(_)
    
    SeqIO.write(std_fasta,std_file,'fasta')


def runCDhit(infile,outfile,threshold='0.999'):
    cd_hitpath = f'{HOME}/anaconda3/bin/cd-hit'

    print('\n============================  Running cd-hit  ============================\n')

    cmd = f'{cd_hitpath} -i {infile} -o {outfile} -c {threshold}'
    runCMD(cmd)

    print('\n============================  End cd-hit  ============================\n')


def runKoFam(infile,outfile):
    kofampath = f'{HOME}/anaconda3/envs/kofamscan/bin/exec_annotation'

    print('\n============================  Running kofamscan  ============================\n')

    cmd = f""". $HOME/anaconda3/etc/profile.d/conda.sh && conda activate kofamscan && \
    time {kofampath} -o {outfile} {infile} -f detail-tsv --report-unannotated"""
    runCMD(cmd)

    print('\n============================  End kofamscan  ============================\n')


def runSelectKoFasta(annofile,infile,outfile):

    print('\n============================  Running select KO annotation  ============================\n')

    df = pd.read_csv(annofile,sep = '\t')
    df = df[df['#'] == '*'].drop_duplicates(subset='gene name')
    acc_ids = list(df['gene name'])
    records = [_ for _ in SeqIO.parse(infile,'fasta') if _.id in acc_ids]
    counts = SeqIO.write(records, outfile, 'fasta')

    print(f'There are {counts} sequences have been annotated.')
    print('\n============================  End select KO  ============================\n')


def runMafft(infile, outfile):
    mafftpath = f'{HOME}/anaconda3/envs/phlan/bin/einsi'

    print('\n============================  Running Mafft  ============================\n')

    cmd = f'{mafftpath} {infile} > {outfile}'
    runCMD(cmd)

    print('\n============================  End Mafft  ============================\n')


def runTrimal(infile,outfile):
    trimalpath = f'{HOME}/anaconda3/envs/phlan/bin/trimal'

    print('\n============================  Running TrimAl  ============================\n')

    cmd = f"{trimalpath} -automated1 -in {infile} -out {outfile}"
    runCMD(cmd)

    print('\n============================  End TrimAl  ============================\n')


def runIQTree(infile, outfile, type):
    iqtreepath = f'{HOME}/anaconda3/envs/phlan/bin/iqtree'

    print('\n============================  Running IQtree  ============================\n')

    if type == 'aa':
        method = 'WAG,LG,JTT,Dayhoff'
    elif type == 'na':
        method = 'GTR+R10'
    
    cmd = f"""{iqtreepath} -nt' AUTO -m MFP -redo mset {method} \
           -mrate E,I,G,I+G -mfreq FU -wbtl -bb 1000 \
           -pre {outfile} -s {infile}"""
    runCMD(cmd)

    print('\n============================  End IQtree  ============================\n')


@click.command()
@click.option("--input", type = str, required = True, default=os.getcwd(), help="input file path.")
@click.option("--type", type = str, default='aa', help="type of fasta. aa or nt. [default = 'aa']")
@click.option("--suffix", type = str, default= 'fasta', help="suffix of fasta file. [default = 'fasta']")
@click.option("--nr", type = str, default='0.999', help="cd-hit nr threshold")
@click.option("--skip_kofam", type=bool, default=False, help="if the kofam results is less than 10, can try to skip this step.")

def main(input, type, suffix, nr, skip_kofam):

    if os.path.isdir(input):
        WD = input
        inputs = glob(os.path.join(input,f'*.{suffix}'))
        if len(inputs) == 1:
            infile = inputs[0]

        else:
            msg = '\n============================'
            msg += '\nInput path is a directory.'
            msg += '\nFind %d .%s files.' % (len(inputs),suffix)
            msg += '\nPlease give an exact name of fasta file using --input and --suffix.'
            msg += '\n============================'
            msg += 'exiting...'
            sys.exit(msg)
    
    elif os.path.islink(input):
        WD = os.path.dirname(input)
        infile = os.readlink(input)

    elif os.path.isfile(input):
        WD = os.path.dirname(input)
        infile = input
    
    else:
        msg = '\n============================'
        msg += '\nPlease give a correct file path of fasta file.'
        msg += '\n============================'
        sys.exit(msg)
    
    file_prefix = os.path.join(WD, os.path.basename(input).split('.')[0])

    std_file = f'{file_prefix}_std.{suffix}'

    try:
        std_infile(infile, std_file)
    except OSError as e:
        sys.exit(e)
    
    print('The input file has been saved to a standard fasta file in %s\n' % std_file)

    nrfile = f'{file_prefix}_nr.{suffix}'
    runCDhit(std_file, nrfile, nr)

    if skip_kofam == False:
        kofamout = f'{file_prefix}_kofam_annotation.out'
        runKoFam(nrfile, kofamout)

        anno_nrfile = f'{file_prefix}_nr.anno.{suffix}'
        runSelectKoFasta(kofamout, nrfile, anno_nrfile)
    else:
        anno_nrfile = nrfile
        print("============================  KOfamscan skipped  ============================")

    align_anno_nrfile = f'{file_prefix}_nr.anno.align.{suffix}'
    runMafft(anno_nrfile, align_anno_nrfile)

    trimal_align_file = f'{file_prefix}_nr.anno.align.trimal.{suffix}'
    runTrimal(align_anno_nrfile,trimal_align_file)

    print('\n============================  trim tree  ============================')
    tree_trimal = f'{file_prefix}_trim'
    if not os.path.exists(tree_trimal):
        os.makedirs(tree_trimal)
    tree_trimal_pre = os.path.join(tree_trimal, 'anno_trimal')
    runIQTree(trimal_align_file, tree_trimal_pre, type)

    print('\n============================  anno tree  ============================')
    tree_anno = f'{file_prefix}_anno'
    if not os.path.exists(tree_anno):
        os.makedirs(tree_anno)
    tree_anno_pre = os.path.join(tree_anno, 'anno_notrim')
    runIQTree(align_anno_nrfile, tree_anno_pre, type)


if __name__ == "__main__":

    main()