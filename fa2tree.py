#!/usr/bin/env python3

import os, subprocess, click, sys
from Bio import SeqIO
from glob import glob
import pandas as pd


HOME = os.getenv('HOME')

def runCMD(cmd):
    print(' '.join(cmd))
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            _out,_err = proc.communicate()
    print(_out,_err)


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
    cmd = [cd_hitpath,'-i',infile,'-o',outfile,'-c',threshold]
    runCMD(cmd)


def runKoFam(infile,outfile):
    kofampath = f'{HOME}/anaconda3/envs/kofamscan/bin/exec_annotation'
    cmd = ['time',kofampath,'-o',outfile,infile,'-f','detail-tsv','--report-unannotated']
    runCMD(cmd)


def runSelectKoFasta(annofile,infile,outfile):
    df = pd.read_csv(annofile,sep = '\t')
    df = df[df['#'] == '*'].drop_duplicates(subset='gene name')
    acc_ids = list(df['gene name'])
    records = [_ for _ in SeqIO.parse(infile,'fasta') if _.id in acc_ids]
    counts = SeqIO.write(records, outfile, 'fasta')
    print(f'There are {counts} sequences have been annotated.')


def runMafft(infile, outfile):
    mafftpath = f'{HOME}/anaconda3/envs/phlan/bin/mafft'
    cmd = [mafftpath, '--auto', infile, '>', outfile]
    runCMD(cmd)


def runTrimal(infile,outfile):
    trimalpath = f'{HOME}anaconda3/envs/phlan/bin/trimal'
    cmd = [trimalpath, '-automated1', '-in', infile, '-out', outfile]
    runCMD(cmd)


def runIQTree(infile, outfile, type):
    iqtreepath = f'{HOME}/anaconda3/envs/phlan/bin/iqtree'
    if type == 'aa':
        method = 'WAG,LG,JTT,Dayhoff'
    elif type == 'na':
        method = 'GTR+R10'
    
    cmd = [iqtreepath, '-nt', 'AUTO', '-m', 'MFP', '-redo', 'mset', method,
           '-mrate', 'E,I,G,I+G', '-mfreq', 'FU', '-wbtl', '-bb', 1000, 
           '-pre', outfile, '-s', infile]
    runCMD(cmd)


@click.command()
@click.option("--input", default=os.getcwd(), help="input file path.")
@click.option("--type", default='aa', help="type of fasta. aa or nt. [default = 'aa']")
@click.option("--suffix", default= 'fasta', help="suffix of fasta file. [default = 'fasta']")
@click.option("--nr", default=0.999, help="cd-hit nr threshold")

def main(input,type,suffix,nr):

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
    
    print('The input file has been saved to a standard fasta file in %s' % std_file)

    nrfile = f'{file_prefix}_nr.{suffix}'
    runCDhit(std_file, nrfile, nr)

    kofamout = f'{file_prefix}_kofam_annotation.out'
    runKoFam(nrfile, kofamout)

    anno_nrfile = f'{file_prefix}_nr.anno.{suffix}'
    runSelectKoFasta(kofamout, nrfile, anno_nrfile)

    align_anno_nrfile = f'{file_prefix}_nr.anno.align.{suffix}'
    runMafft(anno_nrfile, align_anno_nrfile)

    trimal_align_file = f'{file_prefix}_nr.anno.align.trimal.{suffix}'
    runTrimal(align_anno_nrfile,trimal_align_file)

    tree_trimal = f'{file_prefix}_trim'
    if not os.path.exists(tree_trimal):
        os.makedirs(tree_trimal)
    tree_trimal_pre = os.path.join(tree_trimal, 'anno_trimal')
    runIQTree(trimal_align_file, tree_trimal_pre, type)

    tree_anno = f'{file_prefix}_anno'
    if not os.path.exists(tree_anno):
        os.makedirs(tree_anno)
    tree_anno_pre = os.path.join(tree_anno, 'anno_notrim')
    runIQTree(align_anno_nrfile, tree_anno_pre, type)


if __name__ == "__main__":

    main()