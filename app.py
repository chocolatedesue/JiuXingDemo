import os
from datetime import timedelta
from io import BytesIO
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from openpyxl import Workbook
from sqlalchemy.orm import Session

import crud
import restModel
import schemas
from restModel.responseModels import Token, login_exception
from util.convert import convert_templete, \
    convert_db_commit_to_CommitResponse
from util.dbCreator import get_db
from util.restutil import exceptWrapper
from util.tokenManager import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from util.tokenManager import authenticate_user, verify_access_token

if os.getenv("ENV") == "dev":
    app = FastAPI(title="九型人格demo", description="demo接口文档", version="1.0.0")
else:
    app = FastAPI(title="九型人格demo", description="demo接口文档", version="1.0.0", openapi_url=None)


#


@app.post("/api/v1/commit",
          description='''提交测试结果,res为测试结果,
          例如：res = [1,2,3,...9] -> 代表一类得分为1，二类得分为2，三类得分为3，
          ...，九类得分为9, 接口返回分类 用于确定数据保存成功''',
          response_model=restModel.responseModels.CommitInRes,
          responses={400: {"description": "学号已存在 | 测试结果不能全为0 | 分类数组长度不为9",
                           "model": restModel.responseModels.Message},
                     500: {"description": "服务器错误", "model": restModel.responseModels.Message}
                     },
          tags=["学生"]
          )
def add_commit(commit: schemas.Commit, db: Session = Depends(get_db)):
    db_commit = crud.get_commit_by_stu_id(db, commit.stu_id)
    if db_commit:
        raise HTTPException(status_code=400, detail="学号已存在")
    if max(commit.res) == 0:
        raise HTTPException(status_code=400, detail="测试结果不能全为0")
    if len(commit.res) != 9:
        raise HTTPException(status_code=400, detail="测试结果长度不为9")
    try:
        return convert_db_commit_to_CommitResponse(crud.create_commit(db, commit))
    except Exception as e:
        raise HTTPException(status_code=500, detail="服务器错误")


@app.post("/api/v1/addUser",
          description="用于开发时录入用户",
          response_model=restModel.responseModels.Message,
          responses={
              400: {"description": "操作失败", "model": restModel.responseModels.Message},
              401: {"description": "用户名已存在", "model": restModel.responseModels.Message},
              500: {"description": "服务器错误", "model": restModel.responseModels.Message},
          },

          tags=["dev"]
          )
def add_user(user: schemas.User, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    exceptWrapper(crud.create_user, [db, user], "创建失败")
    return {"detail": "创建成功"}


@app.post("/api/v1/login",
          description="登录接口，返回token",
          responses={
              401: {"description": "Incorrect username or password", "model": restModel.responseModels.Message},
              500: {"description": "服务器错误", "model": restModel.responseModels.Message},
          },
          response_model=Token,
          tags=["书院"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_usr = authenticate_user(form_data.username, form_data.password, db)
    if not db_usr:
        raise login_exception
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_usr.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/v1/query",
         description="查询接口，返回指定长度的提交的数据, 如果长度小于limit则返回全部",
         response_model=List[restModel.responseModels.CommitInRes],
         responses={
             401: {"description": "token错误", "model": restModel.responseModels.Message},
             500: {"description": "服务器错误", "model": restModel.responseModels.Message},
         },
         dependencies=[Depends(verify_access_token)],
         tags=["书院"])
def get_commits(limit: int = 50, db: Session = Depends(get_db)):
    res_list = crud.get_commits(db, limit=limit)
    return exceptWrapper(convert_templete, [res_list, convert_db_commit_to_CommitResponse], "查询失败")


@app.delete("/api/v1/deleteById",
            description="删除指定id的提交",
            response_model=restModel.responseModels.Message,
            responses={
                400: {"description": "id不存在", "model": restModel.responseModels.Message},
                401: {"description": "token错误", "model": restModel.responseModels.Message},
                500: {"description": "服务器错误", "model": restModel.responseModels.Message},
            },
            dependencies=[Depends(verify_access_token)],
            tags=["书院"])
def delete_commit(id: int, db: Session = Depends(get_db)):
    if not crud.get_commit_by_id(db, id):
        raise HTTPException(status_code=400, detail="id不存在")
    try:
        crud.delete_commit_by_id(db, id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    return {"detail": "id " + str(id) + ": 删除成功"}


@app.get("/api/v1/queryById",
         description="查询接口，返回指定编号的提交的数据",
         response_model=restModel.responseModels.CommitInRes,
         responses={
             400: {"description": "id不存在", "model": restModel.responseModels.Message},
             401: {"description": "token错误", "model": restModel.responseModels.Message},
             500: {"description": "服务器错误", "model": restModel.responseModels.Message},
         },
         dependencies=[Depends(verify_access_token)],
         tags=["书院"])
def get_commit_by_id(id: int, db: Session = Depends(get_db)):
    if not crud.get_commit_by_id(db, id):
        raise HTTPException(status_code=400, detail="id不存在")
        # raise HTTPException(status_code=400, detail="id不存在")
    return exceptWrapper(convert_db_commit_to_CommitResponse, [crud.get_commit_by_id(db, id)], "查询失败")


@app.get("/api/v1/getExcel",
         description="返回excel文件",
         response_description="返回二进制文件",
         responses={
             401: {"description": "token错误", "model": restModel.responseModels.Message},
             # 403: {"description": "token过期", "model": restModel.responseModels.Message},
             500: {"description": "服务器错误", "model": restModel.responseModels.Message},
         },
         dependencies=[Depends(verify_access_token)],
         tags=["书院"])
def get_docs(db: Session = Depends(get_db)):
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "results"
    excel_title = ["序号", '提交时间', '测试结果', '姓名', '学号', '大类', '辅导员姓名', '一类得分', '二类得分',
                   '三类得分', '四类得分', '五类得分', '六类得分', '七类得分', '八类得分', '九类得分']
    ws1.append(excel_title)

    item_name = ['id', 'time', 'type', 'name', 'stu_id', 'major', 'instructor']

    def get_item(commit: dict):
        item = []
        for i in item_name:
            item.append(commit[i])
        item.extend(list(map(int, commit['res'].split(','))))
        return item

    res_in_db = crud.get_commits(db, flag=True)
    for index, idx in enumerate(range(len(res_in_db)), 1):
        res_in_db[idx].id = index

    for row in range(2, len(res_in_db) + 2):
        item_list = get_item(res_in_db[row - 2].__dict__)
        ws1.append(item_list)

    with BytesIO() as f:
        wb.save(f)
        return StreamingResponse(
            iter([f.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=results.xlsx"}
        )
