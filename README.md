# MondayUpdateScanDate



## 介紹此Repo

Repo的code會放在172.16.6.53這台機器(使用putty登入的帳號密碼可詢問ISCD2負責管VM的人員)，他會在每天早上8點去跑排程，並取得各家客戶的最新送掃時間，並將這個時間回傳至Monday。

Monday URL: https://gssisbu.monday.com/boards/3373985003



## 如何觸發掃描

1. 填寫Org Name
2. 填寫API Token
3. 若您的Org沒有將Fenny加進去，則需要填寫您的User Key


## 維護程式碼

1. 使用putty連線172.16.6.53 , gss/gss@Gss!
2. [修改排程時間]可透過crontab -l 查看排程, crontab -e 編輯排程
3. [修改程式碼]將修改的程式碼放置/home/gss/monday/MondayUpdateScanDate
