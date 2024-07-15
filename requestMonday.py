import json
import requests
import pandas as pd
import warnings
import os
"""

【步驟】
1. 取得此board的資訊 (get_items_detail_by_board_id)
2. 判斷是否為token 資料 (get_required_data_by_board_id)
3. 若是 -> 取得 items id 及 api token資料 (get_required_data_by_board_id)
4. 使用此token 打mend api 取得最後送掃時間
5. 取得後使用monday post method -> board id, item id, value (overwrite_scan_date)

"""

#=============================================================================================
# Base data
# 在 Monday.com 上創建的 API 金鑰
api_key = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI1OTg1ODU3OCwiYWFpIjoxMSwidWlkIjo0MDg5MDY5MCwiaWFkIjoiMjAyMy0wNi0wMVQwMzoxODo1Ny43NTFaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTM2ODU1NDIsInJnbiI6InVzZTEifQ.J6afy_pC2pyFLMCSWl5TOxh2cSfipsfkAQpVh56Oaag"

# 要操作的看板和欄位的 ID
api_key_col_id = "__1"
org_name_col_id = "__15"
user_key_col_id = "text"
# Monday api基本資訊
url = f"https://api.monday.com/v2"
mend_url = f"https://saas.whitesourcesoftware.com/api/v1.3"
headers = {
    "Authorization": api_key,
    'Content-Type': 'application/json'
}
filePath = "Reports/"
#=============================================================================================
# Monday api
def get_items_detail_by_board_id(board_id):
    """根據board id 取得item詳細資訊"""
    payload={
        "query": "query { boards(ids: [" + board_id + ", ]) { items { id column_values { id value text} } } }"
    }
    data=json.dumps(payload)
    response = requests.get(url,headers=headers,data = data)
    return response.json()

def overwrite_scan_date(item_id: str, board_id: str, date):
    """更新最新送掃日期"""
    #先清除
    payload = json.dumps({
    "query": "mutation {change_column_value(item_id: "+item_id +", board_id: "+board_id +", column_id: \"date\", value: \"{\\\"date\\\":\\\"""\\\"}\") {id}}"
    })
    print("[1]enter overwrite_scan_date")
    response = requests.get(url, headers=headers, data=payload)
    print("[1]finish overwrite_scan_date")
    #後寫入
    payload = json.dumps({
    "query": "mutation {change_column_value(item_id: "+item_id +", board_id: "+board_id +", column_id: \"date\", value: \"{\\\"date\\\":\\\""+date+"\\\"}\") {id}}"
    })    
    print("[2]enter overwrite_scan_date")
    response = requests.get(url, headers=headers, data=payload)
    print("[2]finish overwrite_scan_date")
    return response.json()

def overwrite_outdated_version(item_id: str, board_id: str, users):
    #先清除
    payload = json.dumps({
    "query": "mutation {change_column_value(item_id: "+item_id +", board_id: "+board_id +", column_id: long_text, value: \"{\\\"text\\\":\\\"\\\"}\") {id}}"
    })
    response = requests.get(url, headers=headers, data=payload)
    
    #後寫入
    payload = json.dumps({
    "query": "mutation {change_column_value(item_id: "+item_id +", board_id: "+board_id +", column_id: long_text, value: \"{\\\"text\\\":\\\"" + users +"\\\"}\") {id}}"
    })    
    response = requests.get(url, headers=headers, data=payload)
    
    return response.json()

def overwrite_scan_count(item_id: str, board_id: str, cnt: str):
    #先清除
    payload = json.dumps({
    "query": "mutation {change_column_value(item_id: "+item_id +", board_id: "+board_id +", column_id: text0, value: \"\") {id}}"
    })
    response = requests.get(url, headers=headers, data=payload)
    
    #後寫入
    payload = json.dumps({
    "query": "mutation {change_column_value(item_id: "+item_id +", board_id: "+board_id +", column_id: text0, value: \"" + cnt + "\") {id}}"
    })    
    response = requests.get(url, headers=headers, data=payload)
    
    return response.json()

#=============================================================================================
# Mend api
def get_plugin_request_history_report(userKey, orgToken, fileName):
    """
    The Plugin Request History Report provides up-to-date details of all plugin update requests
    for an organization, including whether or not there were policy violations.
    """
    getPluginRequestHistoryReport={
        "requestType":"getPluginRequestHistoryReport",
        "userKey":userKey,
        "orgToken":orgToken
    }     
    print("[1] enter getPluginRequestHistoryReport")
    data=json.dumps(getPluginRequestHistoryReport)
    response = requests.post(mend_url,headers=headers,data = data, timeout=10)
    print("[2] finish reponse getPluginRequestHistoryReport")
    # 檢查回應狀態碼
    if response.status_code == 200:
        # 以二進位方式寫入檔案
        with open(fileName, 'wb') as f:
            f.write(response.content)
            print("[Info] Write successful")
    else:
        print('下載失敗')


#=============================================================================================
# function

#確認Monday返回的response內容(測試用)
def output_json_data(json_data, outputFile="res.json"):
    # 將 JSON 資料寫入到檔案
    with open(outputFile, 'w') as file:
        json.dump(json_data, file)

# 取得此board的所有apiKey及itemId陣列
def get_required_data_by_board_id(board_id):
    """
    根據board id獲取所需資料的apikey和item id陣列
    required_data[index][0] -> apiKey
    required_data[index][1] -> user key
    required_data[index][2] -> item id
    """
    # 取得此board的item資料
    res = get_items_detail_by_board_id(board_id)
    items = res['data']['boards']
    required_data = []  # API金鑰, User Key, 項目ID

    # 判斷是否為token 資料
    for item in items[0]["items"]:
        column_values = item["column_values"] #item 每一個欄位值
        filtered_data = [
            column  # 過濾出包含apikey的column
            for column in column_values
            if (column["id"] == api_key_col_id)
        ]       
        # 如果是apikey，將apikey和item id加入required_data陣列
        api_token = filtered_data[0]['text'] #item api token欄位值
        if len(api_token) > 5:    
            user_key1 = 'fac8afa646b54e70a45fb0c48b4d552bf2ec4f8918cd41fd966ef0bbb456b4a8' #TODO: 先用fenny的               
            user_key = [
                column  # 過濾出包含apikey的column
                for column in column_values
                if (column["id"] == user_key_col_id)
            ][0]['text'] or user_key1

            item_id = item["id"]

            org_name = [
                column  # 過濾出包含apikey的column
                for column in column_values
                if (column["id"] == org_name_col_id)
            ][0]['text']
            
            required_data.append([api_token, user_key, item_id, org_name])
    return required_data

def read_excel(fileName):
    try:
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            data_frame = pd.read_excel(fileName, engine="openpyxl")
    except Exception as e:
        print(e)
        return None
    return data_frame

def get_outdated_version(ScanRecord_version):
    ScanRecord_version['Time'] = pd.to_datetime(ScanRecord_version['Time'])
    # 計算三個月前的日期
    three_month_ago = pd.Timestamp.now() - pd.DateOffset(months=3)
    # 保留近三個月的資料
    ScanRecord_version = ScanRecord_version[ScanRecord_version['Time'] > three_month_ago]
    ScanRecord_version = ScanRecord_version.sort_values('Time').groupby('Requested By').last().reset_index()

    row_count = len(ScanRecord_version)
    outdated_info = pd.DataFrame(index=range(row_count), columns=['Agent', 'Requested By'])
    index = 0

    for i in range(row_count):
        version = ScanRecord_version['Agent'].iloc[i]
        version = version.split(":")[1]
        if(version[0]=='v'):
            version = version.split("v")[1]
        version = version.split(".")[0]
        if(int(version)<23):
            outdated_info.loc[index, 'Agent'] = ScanRecord_version.loc[i, 'Agent']
            outdated_info.loc[index, 'Requested By'] = ScanRecord_version.loc[i, 'Requested By']
            index = index + 1
    outdated_info = outdated_info.dropna()
    if(len(outdated_info)==0):
        return outdated_info
    response = [" ".join(map(str, row)) for index, row in outdated_info.iterrows()]
    response = "\\\\n".join(response)
    
    return response

def get_scan_count(ScanRecord_count):
    ScanRecord_count['Time'] = pd.to_datetime(ScanRecord_count['Time'])
    # 計算三個月前的日期
    three_month_ago = pd.Timestamp.now() - pd.DateOffset(months=3)
    # 保留近三個月的資料
    ScanRecord_count = ScanRecord_count[ScanRecord_count['Time'] > three_month_ago]
    scanCount = ScanRecord_count.shape[0]
    # print("scanCount = ", scanCount)
    return scanCount
#=============================================================================================


def main():
    board_id = "3373985003"
    required_data = get_required_data_by_board_id(board_id) #[apiKey,userkey,itemID]
    #fileName = "latestScan.xlsx"
    # userKey="304684bac7684c4d815ab7753d36360d472753ae6a1c4fa496f534727fdde25b"
    # orgToken="d253d44cfa6046139a9f0d43caea648e6ec496dd94264233b14e35b3e137f729"
    
    for index in range(len(required_data)):
        orgToken = required_data[index][0]
        userKey = required_data[index][1]
        itemId = required_data[index][2]
        org_name = required_data[index][3]
        fileName = filePath + org_name + "_latestScan.xlsx"
        try:
            get_plugin_request_history_report(userKey, orgToken,fileName)
        except:
            print("[Debug] Cannot get the excel file:",org_name)
            pass
        print("[3] finish get_plugin_request_history_report")
        ScanRecord = read_excel(fileName)
        print("[4] finish read ScanRecord")
        try:
            print("[5] enter try")
            print(ScanRecord)
            latest_scan_date = ScanRecord['Time'].head(1).values[0][:10]
            print(latest_scan_date)
            res = overwrite_scan_date(itemId, board_id, latest_scan_date)
            print("Update org latest scan date succeed:", org_name)
            print("Scan date:", latest_scan_date)
        except Exception as e: 
            print(e)
            pass
        
        try:
            outdated_version_users = get_outdated_version(ScanRecord)
            res = overwrite_outdated_version(itemId, board_id, outdated_version_users)
            print("Update org outdated version users succeed:", org_name)
            print("Version and users:")
            print(outdated_version_users)
        except Exception as e: 
            print(e)
            pass

        try:
            scanCount = str(get_scan_count(ScanRecord))
            # print("Scan Count:", scanCount, type(scanCount))
            res = overwrite_scan_count(itemId, board_id, scanCount)
            # print(res)
            print("Update org scan count succeed:", org_name , ": ", scanCount)
        except Exception as e: 
            print(e)
            pass


if __name__ == "__main__":
    main()
