# -*- coding: utf-8 -*-
"""
3면 영상 작품 뷰어 — 목록 만들기
weeks/ 아래 날짜 폴더(예: 2026.11.23)의 학생 HTML을 읽어 manifest.json을 만든다.
파일 이름 규칙: 이름_작품제목.html (학번이 섞여 있어도 화면에는 이름만 보임)
실행: python build_manifest.py
"""
import json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
WEEKS = os.path.join(ROOT, 'weeks')
EMB = re.compile(r'id="scene-embedded">([\s\S]*?)</script>')
VER = re.compile(r'v3badge">(v[0-9.]+)')
DROP = re.compile(r'^(\d{4,}|\(\d+\)|3면스튜디오|v\d+(\.\d+)*|final|최종|최종본|합본|수정본)$', re.I)


def clean_tokens(text, name):
    toks = [t for t in re.split(r'[_\s]+', text) if t]
    out = []
    for t in toks:
        t2 = re.sub(r'\d{8}', '', t)          # 학번(8자리) 제거
        if not t2 or DROP.match(t2) or t2 == name:
            continue
        out.append(t2.replace(name, '') if len(t2) > len(name) else t2)
    return ' '.join(x for x in out if x).strip()


def read_work(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        s = f.read()
    v = VER.search(s)
    m = EMB.search(s)
    info = {'ver': v.group(1) if v else '', 'scenes': 0, 'dur': 0, 'audio': False, 'jsonTitle': ''}
    if m:
        try:
            j = json.loads(m.group(1))
            tl = j.get('timeline') or []
            total = sum(float(it.get('len') or 0) for it in tl)
            for it in tl[:-1]:
                tr = it.get('trans') or {}
                if tr.get('type', 'cut') != 'cut':
                    total -= float(tr.get('dur') or 0)
            lp = j.get('loop') or {}
            if tl and lp.get('type', 'cut') != 'cut':
                total -= float(lp.get('dur') or 0)
            info.update(scenes=len(j.get('scenes') or []), dur=round(max(0, total), 1),
                        audio=bool(j.get('audio')), jsonTitle=j.get('title') or '')
        except Exception as e:
            info['error'] = '작품 데이터를 읽지 못함: %s' % e
    else:
        info['error'] = '3면 스튜디오 작품 파일이 아님'
    return info


DATE = re.compile(r'^(?:(\d{4})[.\-_])?(\d{1,2})[.\-_](\d{1,2})$')   # 2026.11.23 또는 11.09


def date_key(name):
    m = DATE.match(name)
    return (int(m.group(1) or 2026), int(m.group(2)), int(m.group(3))) if m else (0, 0, 0)


def class_order(c):
    order = {'오전반': 0, '오후반': 1}
    return (order.get(c, 9), c)


def scan_works(cdir, sub):
    works = []
    for fn in sorted(os.listdir(cdir)):
        if not fn.lower().endswith(('.html', '.htm')):
            continue
        base = os.path.splitext(fn)[0]
        toks = [t for t in base.split('_') if t]
        name = next((t for t in toks if not re.fullmatch(r'\d+', t)), base)
        name = re.sub(r'\d{6,}', '', name) or name
        info = read_work(os.path.join(cdir, fn))
        title = clean_tokens(base.replace(name, '', 1), name) or clean_tokens(info['jsonTitle'], name)
        works.append({
            'name': name, 'title': title, 'file': sub + fn,
            'size': os.path.getsize(os.path.join(cdir, fn)),
            **{k: info[k] for k in ('ver', 'scenes', 'dur', 'audio')},
            **({'error': info['error']} if 'error' in info else {}),
        })
        print('  %-6s %-28s 씬 %2d · %5.1f초 %s' % (name, title[:28], info['scenes'], info['dur'], info.get('error', '')))
    works.sort(key=lambda w: w['name'])
    return works


def main():
    # weeks 폴더가 있으면 그 안을, 없으면 이 폴더 바로 아래 날짜 폴더(2026.11.23 등)를 읽음
    if os.path.isdir(WEEKS):
        src, prefix = WEEKS, 'weeks/'
    else:
        src, prefix = ROOT, ''
    weeks = []
    for wk in sorted(os.listdir(src), key=date_key, reverse=True):
        wdir = os.path.join(src, wk)
        if not os.path.isdir(wdir) or (prefix == '' and not DATE.match(wk)):
            continue
        # 분반 폴더(오전반·오후반)가 있으면 나눠서, 날짜 폴더에 바로 있는 파일은 '분반 미정'
        groups = [(c, os.path.join(wdir, c), c + '/') for c in sorted(os.listdir(wdir), key=class_order)
                  if os.path.isdir(os.path.join(wdir, c))]
        if any(f.lower().endswith(('.html', '.htm')) for f in os.listdir(wdir)):
            groups.append(('분반 미정', wdir, ''))
        classes = []
        for cname, cdir, sub in groups:
            works = scan_works(cdir, sub)
            if works:
                classes.append({'id': cname, 'works': works})
                print('[%s / %s] %d명' % (wk, cname, len(works)))
        m = DATE.match(wk)
        label = '%d월 %d일' % (int(m.group(2)), int(m.group(3))) if m else wk
        if classes:
            weeks.append({'id': wk, 'label': label, 'classes': classes})
    out = {'title': '2026년 모션그래픽2', 'subtitle': '3면 몰입형 미디어아트 주차별 작품', 'base': prefix, 'updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 'weeks': weeks}
    with open(os.path.join(ROOT, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('manifest.json 저장 완료')


if __name__ == '__main__':
    main()
