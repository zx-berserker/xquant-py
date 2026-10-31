# -*- encoding:utf-8 -*-
"""
date: 2026/10/29
author: Berserker
"""
import zipfile, json, os, requests, io
from config.settings import ROOT_DIR, GlobeConfig
from quant.libs.log import XLog
import pandas as pd
from quant.tool.database.base import SQLAlchemy
from quant.models import Product

cache_dir = os.path.join(ROOT_DIR, 'quant', 'tool', 'cftc', 'cache')
index_path = os.path.join(cache_dir, 'index.json')

class Cot:

    @classmethod
    def cot_zip_file_init(cls):
        zip_file_list = []
        file_dir = os.path.join(ROOT_DIR, 'quant', 'tool', 'cftc', 'file')
        file_list = os.listdir(file_dir)
        for file in file_list:
            name_list = file.split('.')
            if 'zip' in name_list:
                zip_file_list.append(file)
        with open(index_path, 'r', encoding='utf-8') as f:
            index_json = json.load(f)
        try:
            for code in index_json["codes"]:
                tdx_code = code
                cot_code = index_json[code]
                for file in zip_file_list:
                    file_path = os.path.join(file_dir, file)
                    cls.cot_update_from_zip(tdx_code, cot_code, file_path)
        except Exception as e:
            XLog.error(e)


    @classmethod
    def cot_update_from_zip(cls, tdx_code:str, cot_code:str, file_full_name:str):
        csv_path = os.path.join(cache_dir, f'{tdx_code}.csv')
        data_df = pd.DataFrame()
        is_csv_exist = os.path.exists(csv_path)
        data_end_time = None
        data_start_time = None
        if not is_csv_exist:
            open(csv_path, "a").close()
        else:
            try:
                data_df = pd.read_csv(csv_path)
                if len(data_df)>0:
                    data_df['datetime'] = pd.to_datetime(data_df['time'], format='%Y%m%d', errors="coerce")
                    data_df = data_df.set_index('datetime')
                    data_df = data_df.sort_index()
                    data_end_time = data_df.index[-1]
                    data_start_time = data_df.index[0]
            except:
                pass
            
        z = zipfile.ZipFile(file_full_name)
        z.extractall(cache_dir)
        txt = os.path.join(cache_dir, 'f_year.txt')
        if not os.path.exists(txt):
            txt = os.path.join(cache_dir, 'F_Disagg06_16.txt')
        cot_df = pd.read_csv(txt, low_memory=False)
        cot_df = cot_df[cot_df["CFTC_Contract_Market_Code"] == cot_code]
        cot_df = cot_df.filter(['Report_Date_as_YYYY-MM-DD', 'Prod_Merc_Positions_Long_All', 'Prod_Merc_Positions_Short_All',
                         'Swap_Positions_Long_All', 'Swap__Positions_Short_All', 'M_Money_Positions_Long_All', 'M_Money_Positions_Short_All', 
                         'Other_Rept_Positions_Long_All', 'Other_Rept_Positions_Short_All', 'NonRept_Positions_Long_All',
                         'NonRept_Positions_Short_All']) 
        cot_df['pmp'] = cot_df['Prod_Merc_Positions_Long_All'] - cot_df['Prod_Merc_Positions_Short_All']
        cot_df['sp'] = cot_df['Swap_Positions_Long_All'] - cot_df['Swap__Positions_Short_All']
        cot_df['mmp'] = cot_df['M_Money_Positions_Long_All'] - cot_df['M_Money_Positions_Short_All']
        cot_df['orp'] = cot_df['Other_Rept_Positions_Long_All'] - cot_df['Other_Rept_Positions_Short_All']
        cot_df['np'] = cot_df['NonRept_Positions_Long_All'] - cot_df['NonRept_Positions_Short_All']
        cot_df['datetime'] = pd.to_datetime(cot_df['Report_Date_as_YYYY-MM-DD'], format='%Y-%m-%d', errors="coerce")
        cot_df['time'] = cot_df['datetime'].dt.strftime('%Y%m%d')
        cot_df = cot_df.set_index('datetime')
        if data_end_time is not None:
            cot_df = cot_df[(cot_df.index > data_end_time) | (cot_df.index < data_start_time)]
        columns = ['time', 'pmp', 'sp', 'mmp', 'orp', 'np']
        if len(cot_df) > 1:
            if len(data_df) > 0:
                data_df = pd.concat([data_df, cot_df])
            else:
                data_df = cot_df
            data_df = data_df.sort_index()
            data_df.to_csv(csv_path, mode="w", header=True, columns=columns, index=False)
        elif len(cot_df): 
            if is_csv_exist and len(data_df)>0:
                cot_df.tail(1).to_csv(csv_path, mode="a", header=False, columns=columns, index=False)
            else:
                cot_df.tail(1).to_csv(csv_path, mode="a", header=True, columns=columns, index=False)
        try:
            os.remove(txt)
        except:
            pass


    @classmethod
    def cot_update_csv_weekly(cls, year):
        cot_url = "https://cftc.gov/files/dea/history/fut_disagg_txt_" + str(year) + ".zip"
        r = requests.get(cot_url)
        file_path = io.BytesIO(r.content)
        with open(index_path, 'r', encoding='utf-8') as f:
            index_json = json.load(f)
        try:
            for code in index_json["codes"]:
                tdx_code = code
                cot_code = index_json[code]
                cls.cot_update_from_zip(tdx_code, cot_code, file_path)
        except Exception as e:
            XLog.error(e)


    @classmethod
    def cot_update_indicator_weekly(cls):
        count = 240
        startTime = ''
        endTime = ''
        indicator_data = {}
        with open(index_path, 'r', encoding='utf-8') as f:
            index_json = json.load(f)

        for code in index_json["codes"]:
            with SQLAlchemy.session_context() as session:
                product = session.query(Product).filter(
                    Product.tdx_code == code
                ).first()
                if not product:
                    raise Exception(f'Product is None(code:{code}).')
                flex = product.tdx_market.code
            post_data = {
                'code':code, 
                'flex':flex,
                'period': 'WEEKLY',
                'data':[],
                'type': 'AKDJ'
            }
            cache_path = os.path.join(ROOT_DIR, 'quant', 'tool', 'cftc', 'cache', f'{code}.csv')
            try:
                code_indicator_data = {
                    "pmp": '',
                    "sp": '',
                    "mmp": '',
                    "orp": '',
                    "np": '',   
                }

                data_df = pd.read_csv(cache_path, low_memory=False)
                data_df = data_df.tail(count)
                for key in code_indicator_data.keys():
                    for index, row in data_df.iterrows():
                         post_data['data'].append({
                            "Date": row["time"],
                            "Amount": row[key],
                         })                   
                    with requests.Session() as session:
                        post_data_js = json.dumps(post_data, default=int)
                        post_data_js = json.loads(post_data_js)
                        res = session.post('http://127.0.0.1:8025/api/v1/tdx/formula', json=post_data_js)
                        res_json = res.json()

                    if len(res_json['data']) > 2:
                        code_indicator_data[key] = res_json['data']
                indicator_data[code] = code_indicator_data
    
            except Exception as e:
                XLog.print(e)

        indicator_path = os.path.join(cache_dir, 'indicator.json')
        with open(indicator_path, 'w', encoding='utf-8') as file:
            json.dump(indicator_data, file, ensure_ascii=False)


if __name__ == "__main__":
    GlobeConfig.is_log_file = False
    GlobeConfig.is_print = True
    # Cot.cot_update_csv_weekly('2026')
    Cot.cot_update_indicator_weekly()