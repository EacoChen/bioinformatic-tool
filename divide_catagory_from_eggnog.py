#!/usr/bin/env python3
import pandas as pd
import argparse


def parseArgs():
    parser = argparse.ArgumentParser(description='eggnog会注释到多个分类，该脚本把多个分类的序列计数，均匀的分配到各个分类中。不影响总计数值')

    parser.add_argument('-i', '--input', type = str, required=True, help = 'eggnog的注释文件，最后一些是注释的分类')
    parser.add_argument('-o', '--output', type = str, required=False, help = '输出文件')

    return parser.parse_args()


def main():
    args = parseArgs()
    infile = args.input
    output = args.output

    df = pd.read_csv(infile,sep='\t')

    new_df = pd.DataFram(columns=df.columns)

    for x,i in enumerate(df.index):
        if len(df.iat[i,df.shape[1]-1]) > 1:
            _tmp = {}
            for j in range(df.shape[1]):
                if j ==0:
                    _tmp[df.columns[j]] = df.iat[i,j]
                elif j == df.shape[1]-1:
                    for y in range(len(df.iat[i,j])):
                        _tmp[df.columns[j]] = df.iat[i,j][y]
                        new_df = new_df.append(_tmp, ignore_index=True)
                else:
                    _tmp[df.columns[j]] = df.iat[i,j]/len(df.iat[i,df.shape[1]-1])
        else:
            new_df = new_df.append(df.iloc[i], ignore_index=True)

    new_df.to_csv(output,sep='\t',index=False)


if __name__ == '__main__':
    main()