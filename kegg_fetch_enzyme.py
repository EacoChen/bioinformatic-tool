# -*- coding: utf-8 -*-
from Bio.KEGG import REST
from Bio.KEGG import Enzyme
from Bio import SeqIO
from io import StringIO
from tqdm import tqdm
import os
import time


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def home_page(url, AA, NT):
    request = REST.kegg_get(f'ec:{url}')
    record = Enzyme.read(StringIO(request.read()))
    gene_list = record.genes
    gene_query_list = []
    for _ in gene_list:
        for accid in _[1]:
            gene_query_list.append(':'.join([_[0].lower(), accid]))
    query_list = list(divide_chunks(gene_query_list,10))
    save(query_list,AA,NT)


def save(query_list, AA, NT):
    aaseq_record = []
    ntseq_record = []

    for query in tqdm(query_list):
        aaseq_request = REST.kegg_get(query,option='aaseq')
        aaseq_record += [record for record in SeqIO.parse(StringIO(aaseq_request.read()),'fasta')]
        ntseq_request = REST.kegg_get(query,option='ntseq')
        ntseq_record += [record for record in SeqIO.parse(StringIO(ntseq_request.read()),'fasta')]

    aacount = SeqIO.write(aaseq_record,AA,'fasta')
    ntcount = SeqIO.write(ntseq_record,NT,'fasta')
    print(f'共计{aacount}多肽序列，以及{ntcount}核酸序列')


def main():
    url = input('请输入后缀url(错误输入将会导致空白或错误!):')
    start = time.time()
    url_title = url.replace(' ', '').replace('.', '_')  # 字符串操作
    if not os.path.exists(url):
        os.mkdir(url)  # 创建文件夹
    AA_txt = open(f'./{url}/{url_title}_AA.fna', 'w', encoding='utf-8')  # 创建AA txt
    NT_txt = open(f'./{url}/{url_title}_NT.fnn', 'w', encoding='utf-8')  # 创建NT txt
    home_page(url, AA_txt, NT_txt)  # 调用函数开始执行
    AA_txt.close()
    NT_txt.close()
    stop = time.time() - start
    print(f'文件保存在当前目录下，共计{round(stop, 2)} S!')


if __name__ == '__main__':
    main()