import io

P = "public/app.js"
s = io.open(P, encoding="utf-8").read()

anchor = '''  async function eventMove(qq, target) {'''
share = '''  function eventShareImage() {
    const cv = $('eventShareCanvas');
    if (!cv || !eventRoomsState.length) { if ($('eventShareHint')) $('eventShareHint').textContent = '先分房再分享'; return; }
    const w = 1080;
    const pad = 56;
    const roomH = 300;
    const H = 210 + roomH * eventRoomsState.length + 70;
    cv.width = w; cv.height = H;
    const c = cv.getContext('2d');
    const g = c.createLinearGradient(0, 0, w, H);
    g.addColorStop(0, '#ffeef6'); g.addColorStop(.55, '#f2edff'); g.addColorStop(1, '#e9f3ff');
    c.fillStyle = g; c.fillRect(0, 0, w, H);
    const title = ($('eventTitle') && $('eventTitle').textContent) || '包房分配';
    c.fillStyle = '#3a2740';
    c.font = '800 46px "PingFang SC","Microsoft YaHei",sans-serif';
    c.fillText(title.slice(0, 18), pad, 92);
    c.font = '600 24px "PingFang SC","Microsoft YaHei",sans-serif';
    c.fillStyle = '#7a6478';
    const total = eventRoomsState.reduce((n, r) => n + (r.members || []).length, 0);
    c.fillText('共 ' + eventRoomsState.length + ' 间 · ' + total + ' 人 · 按成分匹配度分配', pad, 138);

    eventRoomsState.forEach((r, i) => {
      const y = 180 + i * roomH;
      c.fillStyle = 'rgba(255,255,255,.82)';
      const rr = 26;
      c.beginPath();
      c.moveTo(pad + rr, y); c.arcTo(pad + 940, y, pad + 940, y + roomH - 26, rr);
      c.arcTo(pad + 940, y + roomH - 26, pad, y + roomH - 26, rr);
      c.arcTo(pad, y + roomH - 26, pad, y, rr); c.arcTo(pad, y, pad + 940, y, rr);
      c.closePath(); c.fill();
      c.fillStyle = '#c9366f';
      c.font = '800 30px "PingFang SC","Microsoft YaHei",sans-serif';
      c.fillText('包房 ' + (i + 1), pad + 28, y + 52);
      c.fillStyle = '#6b5b77';
      c.font = '600 22px "PingFang SC","Microsoft YaHei",sans-serif';
      c.fillText((r.members || []).length + ' 人', pad + 150, y + 52);
      c.textAlign = 'right';
      c.fillStyle = '#8a5a7a';
      c.fillText('平均 ' + (r.avg == null ? '—' : r.avg) + '　最高 ' + (r.memberMax == null ? '—' : r.memberMax) + '　最低 ' + (r.memberMin == null ? '—' : r.memberMin), pad + 940 - 28, y + 52);
      c.textAlign = 'left';
      (r.members || []).forEach((m, j) => {
        const col = j % 2, row = Math.floor(j / 2);
        const x = pad + 34 + col * 450;
        const yy = y + 100 + row * 52;
        c.fillStyle = '#4a3a52';
        c.font = '700 26px "PingFang SC","Microsoft YaHei",sans-serif';
        const nm = String(m.name || m.qq || '').slice(0, 10);
        c.fillText(nm, x, yy);
        if (m.avg != null) {
          c.fillStyle = '#c9366f';
          c.fillText(String(m.avg), x + 300, yy);
        }
      });
    });
    c.fillStyle = 'rgba(58,39,64,.55)';
    c.font = '600 20px "PingFang SC","Microsoft YaHei",sans-serif';
    c.fillText('日音成分匹配器 · 按成分相近程度自动分房', pad, H - 34);
    try {
      const url = cv.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = url;
      a.download = '包房分配.png';
      document.body.appendChild(a);
      a.click();
      a.remove();
      if ($('eventShareHint')) $('eventShareHint').textContent = '已生成图片，可在下载里查看/转发。';
    } catch (e) {
      if ($('eventShareHint')) $('eventShareHint').textContent = '生成图片失败：' + (e.message || e);
    }
  }

''' + anchor
assert anchor in s
s = s.replace(anchor, share, 1)

# 记录报名者名字，供手动调房时显示
old_names = '''    const matchedCount = (p.matched_qqs || []).length;'''
new_names = '''    window.__eventNames = {};
    parts.forEach((x) => { if (x.matched && x.qq) window.__eventNames[x.qq] = x.member_name || x.name || x.qq; });
    const matchedCount = (p.matched_qqs || []).length;'''
assert old_names in s
s = s.replace(old_names, new_names, 1)

# 打开详情时恢复上次参数
old_open = '''    renderDetail(payload);
    if ($('eventListCard')) $('eventListCard').hidden = true;'''
new_open = '''    restoreEventParams();
    renderDetail(payload);
    if ($('eventListCard')) $('eventListCard').hidden = true;'''
assert old_open in s
s = s.replace(old_open, new_open, 1)

io.open(P, "w", encoding="utf-8").write(s)
print("share ok")
