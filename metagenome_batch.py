#!/usr/bin/env python3

import os,sys
import click
from glob import glob
from os.path import exists,join
from subprocess import Popen,PIPE


HOME = os.getenv('HOME')

def checkfile(path):

    if not os.path.isdir(path):
        msg = f'Error, {path} is not a directory! use --help to see help'
        sys.exit(msg)
    else:
        ch_path = os.path.abspath(path)
    
    return ch_path


def runCMD(cmd):
    print(' '.join(cmd))
    with Popen(cmd, stdout=PIPE, stderr=PIPE) as proc:
            _out,_err = proc.communicate()
    print(_out,_err)


def runHumann(infile, tmp, out):

    humann_template = open(f'{HOME}/script/humann_template.sh').read()

    for filename in os.listdir(infile):

        jobname = filename.split('.')[0]
        logname = f'{tmp}/humann_{jobname}.%j'
        inname = os.path.join(infile, filename)
        outname = os.path.join(out, jobname)

        sbatch_file = f'{tmp}/humann_{jobname}.sh'
        with open(sbatch_file, 'w') as f:
            f.write(humann_template.format(jobname=jobname,
                                           logname=logname,
                                           inname=inname,
                                           outname=outname))
        
        cmd = ['sbatch', sbatch_file]
        
        runCMD(cmd)


def runSpades(infile, outfile, suffix, tmp, spadestmp='$PFSDIR/metawrap.tmp'):
    
    spades_template = open(f'{HOME}/script/spades_template.sh').read()

    target_path = os.path.join(infile, '*', f'*1.{suffix}')
    
    forward_fastqs = glob(target_path)
    if len(forward_fastqs) == 0:
        msg = f'{target_path} is not exist.'
        sys.exit(msg)

    for forward_fastq in forward_fastqs:
        
        reverse_fastq = forward_fastq.replace(f'1.{suffix}',f'2.{suffix}')
        
        samplename = '_'.join(os.path.basename(forward_fastq).split('_')[:-1])
        jobname = f'{samplename}_spades'
        logname = f'{tmp}/spades_{jobname}.%j'
        outname = f'{outfile}/{samplename}'


        sbatch_file = f'{tmp}/spades_{jobname}.sh'
        with open(sbatch_file, 'w') as f:
            f.write(spades_template.format(jobname=jobname,
                                           logname=logname, 
                                           outname=outname,
                                           file1=forward_fastq,
                                           file2=reverse_fastq,
                                           spadestmp=spadestmp,
                                           tmpfile=outname))

        cmd = ['sbatch', sbatch_file]

        runCMD(cmd)


@click.command()
@click.option("--infile", "infile", default=None, help="input directory path which contains each input file.")
@click.option("--out", "out", default=None, help="output directory path")
@click.option("--tmp", "tmp", default=None, help="give the temporary derectory path")
@click.option("--method", "method", default= None, help="what program we should run. such as [spades,humann]")
@click.option("--suffix", "suffix", default='fastq', help="given the suffix of the input file. default: 'fastq'")

def main(infile, out, tmp, method, suffix):
    infile = checkfile(infile)

    if os.path.exists(out):
        out = os.path.abspath(out)
    else:
        os.makedirs(out)
        out = os.path.abspath(out)
    
    if tmp == None:
        tmp = f'{out}/tmp'
        if not os.path.exists(tmp):
            os.makedirs(f'{out}/tmp')
    else:
        tmp = os.path.abspath(tmp)

    if method == 'humann':
        msg = 'Running HuMANn'
        print(msg)
        suffix = 'fasta'
        runHumann(infile, tmp, out)
    
    elif method == 'spades':
        msg = 'Running spades...'
        print(msg)
        suffix = 'fastq'
        runSpades(infile, out, suffix, tmp)

    
if __name__ == "__main__":
    main()