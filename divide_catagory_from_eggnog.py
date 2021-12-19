#!/usr/bin/env python3
import pandas as pd
import argparse
from tqdm import tqdm


def parseArgs():
    parser = argparse.ArgumentParser(description='eggnog会注释到多个分类，该脚本把多个分类的序列计数，均匀的分配到各个分类中。不影响总计数值')

    parser.add_argument('-i', '--input', type = str, required=True, help = 'eggnog的注释文件，最后一些是注释的分类')
    parser.add_argument('-o', '--output', type = str, required=False, help = '输出文件')
    parser.add_argument('-n', '--stdnum', type = int, required=False, default= 100, help = '计数标准化总值')

    return parser.parse_args()


def main():
    args = parseArgs()
    infile = args.input
    output = args.output
    stdnum = args.stdnum

    df = pd.read_csv(infile,sep='\t')

    data = []

    for x,i in tqdm(enumerate(df.index)):
        if len(df.iat[i,df.shape[1]-1]) > 1:
            _tmp = {}
            for j in range(df.shape[1]):
                if j ==0:
                    _tmp[df.columns[j]] = df.iat[i,j]
                elif j == df.shape[1]-1:
                    for y in range(len(df.iat[i,j])):
                        _tmp[df.columns[j]] = df.iat[i,j][y]
                        data.append(_tmp)
                else:
                    _tmp[df.columns[j]] = df.iat[i,j]/len(df.iat[i,df.shape[1]-1])
        else:
            _tmp = {}
            for j in range(df.shape[1]):
                _tmp[df.columns[j]] = df.iat[i,j]
            data.append(_tmp)

    data_dict = {i:data[i] for i in range(len(data))}
    new_df = pd.DataFrame.from_dict(data_dict,orient='index',columns=df.columns)

    new_df = new_df.groupby[df.columns[-1]].sum()
    new_df.to_csv(f'{output}.count',sep='\t')

    modi_df = pd.DataFrame()
    for column_name in new_df.columns:
        modi_df[column_name] = new_df[column_name]/new_df[column_name].sum()*stdnum

    modi_df.to_csv(f'{output}.tpm',sep='\t')


if __name__ == '__main__':
    main()