const http = require("http");
const fs = require("fs");
const path = require("path");

const LOCAL_PATH = "C:\\Users\\12408\\.qclaw\\workspace\\output\\qclaw_backup_20260328_757e.zip";
const REMOTE_PATH = "backup/qclaw_backup_20260328_757e.zip";
const PORT = 19000;
const HOST = "localhost";

const body = JSON.stringify({
  localPath: LOCAL_PATH,
  remotePath: REMOTE_PATH,
  conflictStrategy: "rename"
});

const options = {
  hostname: HOST,
  port: PORT,
  path: "/proxy/qclaw-cos/upload",
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Content-Length": Buffer.byteLength(body),
  }
};

console.error(`连接 ${HOST}:${PORT}...`);
const req = http.request(options, (res) => {
  let data = "";
  res.on("data", chunk => data += chunk);
  res.on("end", () => {
    console.error(`HTTP ${res.statusCode}`);
    console.log(data);
  });
});

req.on("error", (e) => {
  console.error("请求失败:", e.message);
});

req.write(body);
req.end();
