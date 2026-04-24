#!/usr/bin/env node
/**
 * 自动备份脚本 v3 — 备份到 GitHub 仓库
 * 流程：打包 .qclaw → 推送到 TianT66/anan 仓库 → 删除本地文件
 */
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const WORKSPACE = "C:\\Users\\12408\\.qclaw";
const OUTPUT_DIR = path.join(__dirname, "..", "output");
const REPO_DIR = path.join(__dirname, "..", "repos", "anan");
const DATE_STR = new Date().toISOString().slice(0, 10).replace(/-/g, "");
const BACKUP_NAME = `qclaw_backup_${DATE_STR}_${crypto.randomBytes(2).toString("hex")}.zip`;

function log(msg) { console.error(`[backup ${new Date().toISOString().slice(11,19)}] ${msg}`); }

function exec(cmd, opts = {}) {
  return execSync(cmd, { shell: "cmd", encoding: "utf8", ...opts });
}

/** CRC32 */
function crc32(data) {
  let crc = 0xFFFFFFFF;
  const table = makeCrcTable();
  for (let i = 0; i < data.length; i++) crc = (crc >>> 8) ^ table[(crc ^ data[i]) & 0xFF];
  return (crc ^ 0xFFFFFFFF) >>> 0;
}
function makeCrcTable() {
  const t = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let j = 0; j < 8; j++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
    t[i] = c;
  }
  return t;
}

/** 纯 Node.js 创建 ZIP */
function createZip(entries) {
  const parts = [], cd = [];
  let offset = 0;
  for (const e of entries) {
    const nameBuf = Buffer.from(e.name.replace(/\\/g, "/"), "utf8");
    const compressed = require("zlib").deflateSync(e.data);
    const crc = crc32(e.data);
    const lh = Buffer.alloc(30 + nameBuf.length);
    lh.writeUInt32LE(0x04034b50, 0); lh.writeUInt16LE(20, 4); lh.writeUInt16LE(0, 6);
    lh.writeUInt16LE(8, 8); lh.writeUInt32LE(crc, 14);
    lh.writeUInt32LE(compressed.length, 18); lh.writeUInt32LE(e.data.length, 22);
    lh.writeUInt16LE(nameBuf.length, 26); lh.writeUInt16LE(0, 28);
    nameBuf.copy(lh, 30);
    const ce = Buffer.alloc(46 + nameBuf.length);
    ce.writeUInt32LE(0x02014b50, 0); ce.writeUInt16LE(20, 4); ce.writeUInt16LE(20, 6);
    ce.writeUInt16LE(0, 8); ce.writeUInt16LE(8, 10); ce.writeUInt32LE(crc, 16);
    ce.writeUInt32LE(compressed.length, 20); ce.writeUInt32LE(e.data.length, 24);
    ce.writeUInt16LE(nameBuf.length, 28); ce.writeUInt16LE(0, 30);
    ce.writeUInt32LE(0, 38); ce.writeUInt32LE(offset, 42);
    nameBuf.copy(ce, 46);
    cd.push(ce); parts.push(lh, compressed);
    offset += lh.length + compressed.length;
  }
  const cdData = Buffer.concat(cd);
  parts.push(cdData);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0); eocd.writeUInt16LE(entries.length, 8);
  eocd.writeUInt16LE(entries.length, 10); eocd.writeUInt32LE(cdData.length, 12);
  eocd.writeUInt32LE(offset, 16); parts.push(eocd);
  return Buffer.concat(parts);
}

/** 遍历目录 */
const SKIP = new Set([".git","node_modules",".cache","browser\\openclaw\\user-data\\BrowserMetrics","browser\\openclaw\\user-data\\Crashpad"]);
function walk(dir, base) {
  const r = [];
  try {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, e.name), rel = path.relative(base, full);
      if (e.isDirectory()) {
        if (SKIP.has(e.name) || SKIP.has(rel)) continue;
        try { r.push(...walk(full, base)); } catch {}
      } else {
        try { r.push({ name: rel.replace(/\\/g, "/"), data: fs.readFileSync(full) }); } catch {}
      }
    }
  } catch {}
  return r;
}

function main() {
  log(`扫描 ${WORKSPACE}`);
  const entries = walk(WORKSPACE, WORKSPACE);
  const rawSize = entries.reduce((s, e) => s + e.data.length, 0);
  log(`共 ${entries.length} 文件，原始 ${(rawSize/1024/1024).toFixed(1)} MB`);

  log(`创建 ZIP...`);
  const zipData = createZip(entries);
  log(`ZIP 大小 ${(zipData.length/1024/1024).toFixed(1)} MB`);

  // 写入 repo
  const zipPath = path.join(REPO_DIR, BACKUP_NAME);
  fs.writeFileSync(zipPath, zipData);
  log(`已写入 ${zipPath}`);

  // git add + commit
  log(`提交...`);
  try { exec(`git -C "${REPO_DIR}" add ${BACKUP_NAME}`); } catch {}
  const msg = `backup: qclaw ${new Date().toISOString().slice(0,10)} (${entries.length} files)`;
  try {
    exec(`git -C "${REPO_DIR}" commit -m "${msg}"`);
  } catch (e) {
    // 可能没有变更
    const out = e.stdout || "";
    if (out.includes("nothing to commit")) {
      log("无新变更，跳过提交");
      fs.unlinkSync(zipPath);
      console.log(JSON.stringify({ success: true, skipped: true, message: "无新变更，已删除本地临时文件" }));
      return;
    }
  }

  // push
  log(`推送 GitHub...`);
  try {
    exec(`git -C "${REPO_DIR}" push origin main`);
  } catch (e) {
    log(`推送失败: ${e.message}`);
    console.log(JSON.stringify({ success: false, error: "GitHub push failed: " + e.message }));
    return;
  }

  // 删除本地 ZIP
  try { fs.unlinkSync(zipPath); log("本地 ZIP 已删除"); } catch {}

  console.log(JSON.stringify({
    success: true,
    backupName: BACKUP_NAME,
    filesCount: entries.length,
    zipSizeMB: (zipData.length/1024/1024).toFixed(1),
    repo: "github.com/TianT66/anan",
    timestamp: new Date().toISOString(),
  }));
}

main().catch(err => { log(`异常: ${err.message}`); process.exit(1); });
