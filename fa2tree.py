#!/usr/bin/env python3

import os, subprocess, click, sys
from Bio import SeqIO
from glob import glob


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


def runCDhit(infile,outfile):
    for 


@click.command()
@click.option("--input", default=os.getcwd(), help="input file path.")
@click.option("--type", default='aa', help="type of fasta. aa or nt. [default = 'aa']")
@click.option("--suffix", default= 'fasta', help="suffix of fasta file. [default = 'fasta']")

def main(input,type,suffix):
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

    std_file = os.path.join(file_prefix, f'_std.{suffix}')

    try:
        std_infile(infile, std_file)
    except OSError as e:
        sys.exit(e)
    
    print('The input file has been saved to a standard fasta file in %s' % std_file)

    outfile = f'{file_prefix}/'
    runCDhit(std_file, outfile)


if __name__ == "__main__":

    main()