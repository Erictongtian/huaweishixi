import subprocess, time, sys, json, urllib.request

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"],
    cwd="D:/huawei/AssetMgmt/backend",
)
time.sleep(5)

BASE = "http://localhost:8007/api/v1"
TS = str(int(time.time()))


def api(method, path, data=None, token=None):
    url = BASE + path
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        resp = urllib.request.urlopen(req)
        if resp.status == 204:
            return 204, {}
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"message": body}


passed = 0
failed = 0

def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print("  PASS: " + name)
    else:
        failed += 1
        print("  FAIL: " + name)


print("=== 1. 注册 ===")
s, r = api("POST", "/auth/register", {"username": "e2eb_" + TS, "password": "Test123456", "nickname": "买家E2E"})
check("注册买家", s == 201)
s, r = api("POST", "/auth/register", {"username": "e2es_" + TS, "password": "Test123456", "nickname": "卖家E2E"})
check("注册卖家", s == 201)

print("=== 2. 登录 ===")
s, r = api("POST", "/auth/login", {"username": "e2es_" + TS, "password": "Test123456"})
seller_token = r["data"]["access_token"]
seller_id = r["data"]["user"]["id"]
check("卖家登录", s == 200)

s, r = api("POST", "/auth/login", {"username": "e2eb_" + TS, "password": "Test123456"})
buyer_token = r["data"]["access_token"]
buyer_id = r["data"]["user"]["id"]
check("买家登录", s == 200)

print("=== 3. 获取分类 ===")
s, r = api("GET", "/categories", token=buyer_token)
categories = r["data"]
cat_id = categories[0]["id"]
check("获取分类列表", s == 200 and len(categories) > 0)

print("=== 4. 发布设备 ===")
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body_str = (
    "--" + boundary + "\r\n"
    'Content-Disposition: form-data; name="title"\r\n\r\nE2E测试设备2\r\n'
    "--" + boundary + "\r\n"
    'Content-Disposition: form-data; name="category_id"\r\n\r\n' + str(cat_id) + "\r\n"
    "--" + boundary + "\r\n"
    'Content-Disposition: form-data; name="price"\r\n\r\n99.99\r\n'
    "--" + boundary + "\r\n"
    'Content-Disposition: form-data; name="condition_level"\r\n\r\nalmost_new\r\n'
    "--" + boundary + "--\r\n"
)
req = urllib.request.Request(BASE + "/devices", data=body_str.encode(), method="POST")
req.add_header("Content-Type", "multipart/form-data; boundary=" + boundary)
req.add_header("Authorization", "Bearer " + seller_token)
resp = urllib.request.urlopen(req)
device_data = json.loads(resp.read().decode())["data"]
device_id = device_data["id"]
check("发布设备", device_data["status"] == "on_sale")

print("=== 5. 查看设备详情 ===")
s, r = api("GET", "/devices/" + str(device_id), token=buyer_token)
check("设备详情", s == 200 and r["data"]["title"] == "E2E测试设备2")

print("=== 6. 买家下单 ===")
s, r = api("POST", "/orders", {"device_id": str(device_id), "buyer_message": "E2E测试购买"}, token=buyer_token)
order_id = r["data"]["id"]
check("下单成功", s == 201 and r["data"]["status"] == "pending")

print("=== 7. 卖家确认 ===")
s, r = api("PATCH", "/orders/" + str(order_id) + "/confirm", {"seller_remark": "确认发货"}, token=seller_token)
check("确认订单", s == 200 and r["data"]["status"] == "confirmed")

print("=== 8. 买家确认交付 ===")
s, r = api("PATCH", "/orders/" + str(order_id) + "/complete", token=buyer_token)
check("确认交付", s == 200 and r["data"]["status"] == "completed")

print("=== 9. 买家评价 ===")
s, r = api("POST", "/reviews", {"order_id": str(order_id), "rating": 5, "content": "E2E测试好评"}, token=buyer_token)
check("创建评价", s == 201 and r["data"]["rating"] == 5)

print("=== 10. 查看设备评价 ===")
s, r = api("GET", "/devices/" + str(device_id) + "/reviews")
check("设备评价列表", s == 200 and r["data"]["total"] >= 1)

print("=== 11. 卖家评价统计 ===")
s, r = api("GET", "/users/" + str(seller_id) + "/review-stats")
check("评价统计", s == 200 and r["data"]["avg_rating"] > 0)

print("=== 12. 个人中心-更新信息 ===")
s, r = api("PUT", "/users/me", {"nickname": "卖家E2E更新"}, token=seller_token)
check("更新个人信息", s == 200 and r["data"]["nickname"] == "卖家E2E更新")

print("=== 13. 修改密码 ===")
s, r = api("PUT", "/users/me/password", {"old_password": "Test123456", "new_password": "Newpass123"}, token=buyer_token)
check("修改密码", s == 200)

print("=== 14. 我的发布 ===")
s, r = api("GET", "/users/me/devices", token=seller_token)
check("我的发布列表", s == 200 and r["data"]["total"] >= 1)

print("=== 15. 分类管理(管理员) ===")
s, r = api("POST", "/auth/login", {"username": "admin", "password": "Admin123456"})
admin_token = r["data"]["access_token"]
s, r = api("POST", "/categories", {"name": "E2E新分类_" + str(int(time.time())), "sort_order": 99}, token=admin_token)
check("创建分类", s == 201)
new_cat_id = r["data"]["id"]
s, r = api("PUT", "/categories/" + str(new_cat_id), {"name": "E2E更新分类"}, token=admin_token)
check("更新分类", s == 200)
s, r = api("DELETE", "/categories/" + str(new_cat_id), token=admin_token)
check("删除分类", s == 204)

print("=== 16. 重复评价约束 ===")
s, r = api("POST", "/reviews", {"order_id": str(order_id), "rating": 3}, token=buyer_token)
check("重复评价被拒", s == 409)

print("=== 17. 已售设备再次下单 ===")
s, r = api("POST", "/orders", {"device_id": str(device_id)}, token=buyer_token)
check("已售设备下单被拒", s in (400, 409))

print("=== 18. 非买家评价被拒 ===")
s, r = api("GET", "/orders/" + str(order_id), token=seller_token)
s2, r2 = api("POST", "/reviews", {"order_id": str(order_id), "rating": 4}, token=seller_token)
check("卖家评价被拒", s2 == 403)

print()
print("=" * 40)
print("PASSED: " + str(passed) + " / " + str(passed + failed))
print("FAILED: " + str(failed))

proc.terminate()