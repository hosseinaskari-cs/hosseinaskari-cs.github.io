#!/usr/bin/env python3
"""Prepare a clean al-folio site from Yadan Luo's public MIT-licensed source.
Run from repository root: python3 prepare_academic_site.py
No old website files are copied into the generated site.
"""
import os, re, shutil, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_academic_source'
UPSTREAM = 'https://github.com/Luoyadan/luoyadan.github.io.git'

def put(rel, contents):
    p = OUT / rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(contents.strip() + '\n', encoding='utf-8')

def copy(src, rel):
    p = src / rel
    if not p.exists(): return
    dest = OUT / rel; dest.parent.mkdir(parents=True, exist_ok=True)
    if p.is_dir(): shutil.copytree(p, dest, dirs_exist_ok=True)
    else: shutil.copy2(p, dest)

def pdf_figure_to_png(source, destination):
    """Rasterize the first page of a figure PDF, preserving its aspect ratio."""
    converter = shutil.which('pdftoppm')
    if not converter and os.environ.get('GITHUB_ACTIONS') == 'true':
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'poppler-utils'], check=True)
        converter = shutil.which('pdftoppm')
    if not converter:
        raise RuntimeError('PDF figures require pdftoppm (poppler-utils); alternatively upload PNG figures.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([converter, '-f', '1', '-l', '1', '-singlefile', '-cropbox',
                    '-scale-to', '1400', '-png', str(source), str(destination.with_suffix(''))], check=True)
    if not destination.is_file() or destination.stat().st_size == 0:
        raise RuntimeError('Could not render publication figure: ' + str(source))

def prepare(src):
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    for rel in ['_includes','_layouts','_sass','_plugins','assets/css','assets/js','assets/fonts','assets/webfonts','assets/libs','Gemfile','Gemfile.lock','LICENSE','LICENSE.md']:
        copy(src, rel)
    for rel in ['_layouts/about.html','_layouts/default.html','_includes/social.html','assets/css/main.scss','Gemfile']:
        if not (OUT / rel).is_file(): raise RuntimeError('Upstream changed: missing '+rel)
    config = (src/'_config.yml').read_text()
    settings = {'title':'blank','first_name':'Hossein','middle_name':'','last_name':'Askari','email':'h.askari@uq.edu.au','description':'Generative models, Bayesian inference, and computational imaging.','footer_text':'Powered by Jekyll and al-folio.','keywords':'diffusion models, flow matching, inverse problems, computational imaging','icon':'HA','url':'https://hosseinaskari-cs.github.io','baseurl':'','github_username':'hosseinaskari-cs','cv_url':'','linkedin_username':'','scholar_userid':'ZNLvHpoAAAAJ','orcid_id':'0000-0002-0838-9183','google_analytics':'','panelbear_analytics':'','google_site_verification':'','bing_site_verification':'','blog_name':'Research Notes','blog_description':'','enable_google_analytics':'false','enable_panelbear_analytics':'false','enable_google_verification':'false','enable_bing_verification':'false','enable_darkmode':'true','navbar_fixed':'true','footer_fixed':'false','max_width':'1080px','news_limit':'6','enable_masonry':'false','enable_medium_zoom':'false','serve_og_meta':'false','serve_schema_org':'false','disqus_shortname':''}
    # Do not inherit other people's optional account IDs or contact text.
    original_social = (src / '_includes/social.html').read_text(encoding='utf-8')
    for key in re.findall(r'{%-?\s*if site\.([a-zA-Z_][a-zA-Z0-9_]*)\s*-?%}', original_social):
        settings.setdefault(key, '')
    settings['contact_note'] = ''
    settings['rss_icon'] = 'false'
    for k,v in settings.items():
        # Replace complete top-level scalar (including indented block for description/footer).
        pattern = rf'(?m)^{re.escape(k)}:[^\n]*(?:\n[ \t]+[^\n]*)*' if k in ('description','footer_text') else rf'(?m)^{re.escape(k)}:[^\n]*'
        val = k+': '+v
        config,n = re.subn(pattern,lambda _:val,config,count=1)
        if not n: config += '\n'+val+'\n'
    config = re.sub(r'(?m)^  last_name:.*$', '  last_name: [Askari]',config)
    config = re.sub(r'(?m)^  first_name:.*$', '  first_name: [Hossein]',config)
    # Favicon text uses one emoji, no borrowed logo.
    config = config.replace('icon: HA','icon: "🔬"')
    put('_config.yml',config)
    put('_layouts/about.html', """---
layout: default
---
<div class="post ha-home">
  <article>
    <header class="ha-hero">
      <div class="ha-bio">
        <h1 class="ha-name"><span style="font-weight:700;">{{ site.first_name }}</span> {{ site.last_name }}</h1>
        <p>I am a researcher in <strong>machine learning, computer vision, and medical imaging</strong>. I recently completed my PhD in Computer Science at <a href="https://www.uq.edu.au/">The University of Queensland (UQ)</a>, Australia, under the supervision of <a href="https://sunhongfu.github.io/">Dr. Hongfu Sun</a> and <a href="https://people.smp.uq.edu.au/FredRoosta/">Prof. Fred Roosta</a>. Prior to my PhD, I completed my Master’s by Research at the <a href="https://www.adelaide.edu.au/aiml/">Australian Institute for Machine Learning (AIML)</a>, Adelaide University, under the supervision of <a href="https://researchers.adelaide.edu.au/profile/gustavo.carneiro">Prof. Gustavo Carneiro</a>.</p>
      </div>
      {% if page.profile.image %}<img class="ha-photo" src="{{ page.profile.image | prepend: '/assets/img/' | relative_url }}" alt="Hossein Askari">{% endif %}
    </header>
    <div class="ha-intro">{{ content }}</div>
    {% include ha-interests.html %}
    <div class="ha-opportunities">I welcome research collaborations and am interested in postdoctoral and research scientist opportunities. Please feel free to <a href="mailto:{{ site.email }}">contact me</a>.</div>
    <!-- UPSTREAM_SOCIAL_BLOCK -->
    <div class="ha-news-selected">
      {% if page.news %}{% include news.html %}{% endif %}
      {% if page.selected_papers %}{% include selected_papers.html %}{% endif %}
    </div>
  </article>
</div>""")
    # Reuse the original social wrapper verbatim, not a hand-built approximation.
    upstream_about = (src / '_layouts/about.html').read_text(encoding='utf-8')
    wrapper = re.search(r'{%-?\s*if page\.social\s*-?%}.*?{%-?\s*endif\s*-?%}', upstream_about, flags=re.S)
    if wrapper is None or 'class="contact-icons"' not in wrapper.group() or '{% include social.html %}' not in wrapper.group():
        raise RuntimeError('Upstream social wrapper changed; inspect before publishing.')
    about = (OUT / '_layouts/about.html').read_text(encoding='utf-8')
    put('_layouts/about.html', about.replace('<!-- UPSTREAM_SOCIAL_BLOCK -->', wrapper.group()))
    put('_includes/ha-interests.html', """<section class="ha-interests" aria-labelledby="ha-interests-title">
<h2 id="ha-interests-title" class="ha-sr-only">Research Interests</h2>
<div class="ha-interest-grid">
<div class="ha-interest-card">
<i class="fas fa-project-diagram ha-interest-icon" aria-hidden="true"></i>
<div><h3>Out-of-Distribution Generalization</h3>
<ul><li>Domain adaptation</li><li>Task adaptation</li><li>Domain generalization</li><li>Test-time adaptation</li></ul></div>
</div>
<div class="ha-interest-card">
<i class="fas fa-brain ha-interest-icon" aria-hidden="true"></i>
<div><h3>In-Distribution Generalization</h3>
<ul><li>Learning with noisy labels</li><li>Robust learning</li><li>Limited supervision</li></ul></div>
</div>
<div class="ha-interest-card">
<i class="fas fa-wave-square ha-interest-icon" aria-hidden="true"></i>
<div><h3>Inverse Problems</h3>
<ul><li>Medical image reconstruction</li><li>Image restoration</li><li>Computational imaging</li></ul></div>
</div>
<div class="ha-interest-card">
<i class="fas fa-random ha-interest-icon" aria-hidden="true"></i>
<div><h3>Generative Models</h3>
<ul><li>Diffusion models</li><li>Flow matching</li><li>Normalizing flows</li><li>Generative inference</li></ul></div>
</div>
<div class="ha-interest-card">
<i class="fas fa-layer-group ha-interest-icon" aria-hidden="true"></i>
<div><h3>Foundation Models &amp; Multimodal Learning</h3>
<ul><li>Vision-language models (VLMs)</li><li>Foundation model adaptation</li><li>Multimodal learning</li><li>Transfer learning</li></ul></div>
</div>
<div class="ha-interest-card">
<i class="fas fa-chart-line ha-interest-icon" aria-hidden="true"></i>
<div><h3>Bayesian Inference &amp; Optimization</h3>
<ul><li>Posterior sampling</li><li>Variational inference</li><li>Uncertainty quantification</li><li>Stochastic optimization</li></ul></div>
</div>
</div>
</section>""")
    default = (OUT/'_layouts/default.html').read_text()
    default = re.sub(r'\s*<!-- Google tag \(gtag.js\) -->.*?</script>\s*<script>.*?</script>', '',default,flags=re.S)
    if 'G-YB1TEJT0Y8' in default: raise RuntimeError('Cannot remove upstream analytics tag')
    put('_layouts/default.html',default)
    # Keep upstream social.html, including its original Font Awesome / Academicons classes.
    social = (src / '_includes/social.html').read_text(encoding='utf-8')
    cv = re.search(r'<a\b[^>]*href="/assets/pdf/Yadan_latest_Resume_2026v4\.pdf"[^>]*>.*?</a>', social, flags=re.S)
    if cv is None:
        raise RuntimeError('Upstream CV markup changed; inspect before publishing.')
    if (ROOT / 'academic-assets/cv.pdf').is_file():
        social = social[:cv.start()] + cv.group().replace('/assets/pdf/Yadan_latest_Resume_2026v4.pdf', '/assets/pdf/cv.pdf') + social[cv.end():]
    else:
        social = social[:cv.start()] + social[cv.end():]
    # UQ is an existing personal website link; reuse the same icon font and upstream styling.
    social += '\n<a href="https://www.uq.edu.au/" title="UQ"><i class="fas fa-university elegant-icon"></i></a>\n'
    put('_includes/social.html', social)
    put('_includes/footer.html', '''<footer class="{% if site.footer_fixed %}fixed-bottom{% else %}sticky-bottom{% endif %}"><div class="container mt-0">&copy; {{ site.time | date: '%Y' }} Hossein Askari. Powered by <a href="https://github.com/alshedivat/al-folio">al-folio</a>.</div></footer>''')
    put('_pages/about.md', """---
layout: about
title: About
permalink: /
subtitle: Machine learning, computer vision, and medical imaging
profile:
  align: right
  image: profile.svg
  image_circular: false
  address:
news: true
selected_papers: true
social: true
---
My recent research focuses on **generative inference under partial and distribution-shifted information**, with applications to **inverse problems** and **domain adaptation**. My broader research interests span the following areas:
""")
    with (OUT/'assets/css/main.scss').open('a', encoding='utf-8') as css:
        css.write("""
/* Compact, full-width home layout inspired by the provided reference. */
.ha-home { max-width: 920px; margin: 0 auto; }
.ha-home .ha-hero { display: grid; grid-template-columns: minmax(0,1fr) 200px; gap: 30px; align-items: start; margin: 0 0 1.05rem; padding-right: 48px; }
.ha-home .ha-name { font-size: 2.35rem; font-weight: 300; line-height: 1.15; margin: 0 0 0.9rem; }
.ha-home .ha-bio p { margin: 0 0 0.65rem; line-height: 1.5; }
.ha-home .ha-photo { width: 200px; height: 200px; object-fit: cover; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,.18); }
.ha-home .ha-intro { margin: 0 0 0.8rem; }
.ha-home .ha-intro p { margin: 0; line-height: 1.5; }
.ha-home .ha-intro strong { color: var(--global-theme-color,#ad2ba1); }
.ha-home .ha-interests { width: 100%; margin: 0 0 1rem; padding: 0; }
.ha-home .ha-sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
.ha-home .ha-interest-grid { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 12px; align-items: stretch; }
.ha-home .ha-interest-card { box-sizing: border-box; display: grid; grid-template-columns: 26px minmax(0,1fr); column-gap: 12px; align-items: start; padding: 12px 14px 12px 18px; border: 1px solid var(--global-divider-color,#dedede); border-radius: 8px; min-width: 0; background: var(--global-bg-color,#fff); transition: border-color .18s ease; }
.ha-home .ha-interest-card:hover { border-color: var(--global-theme-color,#ad2ba1); }
.ha-home .ha-interest-card > div { min-width: 0; }
.ha-home .ha-interest-card .ha-interest-icon { color: var(--global-theme-color,#ad2ba1); font-size: 17px; margin: 5px 0 0; text-align: center; line-height: 1; }
.ha-home .ha-interest-card h3 { color: var(--global-text-color,#222); font-size: 14px; font-weight: 700; line-height: 1.22; margin: 0 0 4px; padding: 0; }
.ha-home .ha-interest-card ul { list-style: none; font-size: 12px; font-weight: 400; line-height: 1.48; margin: 0; padding: 0; }
.ha-home .ha-interest-card li { margin: 0; padding: 0 0 0 8px; position: relative; }
.ha-home .ha-interest-card li::before { content: "•"; position: absolute; left: 0; font-size: 10px; }
.ha-home .ha-opportunities { font-size: .95rem; line-height: 1.5; padding: 10px 16px; border-radius: 5px; background: rgba(173,43,161,.075); margin: 0 0 1.4rem; }
/* Academic services page; use the existing theme accent. */
.ha-services h3 { font-size: 1.15rem; font-weight: 700; margin: 1.4rem 0 .8rem; }
.ha-services h3::after { content: ""; display: block; width: 65px; height: 2px; margin-top: 7px; background: linear-gradient(90deg, var(--global-theme-color,#ad2ba1), transparent); }
.ha-services ul { padding-left: 1.25rem; }
.ha-services li { margin-bottom: .6rem; }
.ha-services li::marker { color: var(--global-theme-color,#ad2ba1); }
.ha-home .ha-news-selected { border-top: 1px solid var(--global-divider-color,#eee); padding-top: .8rem; }
.ha-home .ha-news-selected .news h2 { color: var(--global-theme-color,#ad2ba1); font-size: 1.2rem; font-weight: 700; }
@media(max-width: 767px) { .ha-home .ha-hero { grid-template-columns: minmax(0,1fr) 140px; gap: 16px; padding-right: 0; } .ha-home .ha-photo { width: 140px; height: 140px; } .ha-home .ha-interest-grid { grid-template-columns: repeat(2,minmax(0,1fr)); } }
@media(max-width: 500px) { .ha-home .ha-hero { grid-template-columns: minmax(0,1fr) 92px; gap: 12px; } .ha-home .ha-photo { width: 92px; height: 92px; } .ha-home .ha-name { font-size: 1.85rem; } .ha-home .ha-interest-grid { grid-template-columns: 1fr; } }
""")
    # Preserve Yadan's actual publication filtering page, with new topical data.
    pubs = (src/'_pages/publications.md').read_text()
    pubs = re.sub(r'(?m)^description:.*$', 'description: Selected research publications, organized by year and topic.',pubs)
    put('_pages/publications.md',pubs)
    put('_pages/research.md', '''---
layout: page
permalink: /research/
title: Research
description: Research interests in machine learning, computer vision, and medical imaging.
nav: true
nav_order: 2
---
## Out-of-Distribution Generalization
Domain adaptation, task adaptation, domain generalization, and test-time adaptation.

## In-Distribution Generalization
Learning with noisy labels and robust learning, with an emphasis on label-noise robustness.

## Inverse Problems
Medical image reconstruction (MRI and CT), image restoration, computational imaging, and generative posterior sampling using diffusion models and flow matching.

## Generative Models
Diffusion models, flow matching, normalizing flows, and generative inference.

## Foundation Models & Multimodal Learning
Emerging research interests in vision-language models, foundation model adaptation, multimodal representation learning, and transfer learning.

## Bayesian Inference & Optimization
Posterior sampling, variational inference, uncertainty quantification, and stochastic optimization.

### Research projects

- **[LFlow](https://github.com/hosseinaskari-cs/LFlow)** — latent flow-matching inference for linear inverse problems (NeurIPS 2025).
- **[BGDM](https://github.com/hosseinaskari-cs/BGDM)** — bi-level diffusion guidance for MRI and CT reconstruction (WACV 2025).
- **[MapFlow](https://doi.org/10.1007/s10994-023-06357-2)** — latent transitions for unsupervised domain adaptation (*Machine Learning*, 2023).''')
    put('_pages/services.md', '''---
layout: page
permalink: /services/
title: Services
nav: true
nav_order: 3
---

<div class="ha-services" markdown="1">

### Conference Reviewer

- Conference on Neural Information Processing Systems (NeurIPS)
- IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)

</div>
''')
    put('_pages/contact.md', '''---
layout: page
permalink: /contact/
title: Contact
nav: true
nav_order: 4
---
I welcome enquiries about research collaborations and research career opportunities.

**Academic email:** [h.askari@uq.edu.au](mailto:h.askari@uq.edu.au)

**GitHub:** [hosseinaskari-cs](https://github.com/hosseinaskari-cs)

Brisbane, Australia.''')
    put('_bibliography/papers.bib', '''@inproceedings{askari2025lflow,
 title={Latent Refinement via Flow Matching for Training-free Linear Inverse Problem Solving},
 author={Askari, Hossein and Luo, Yadan and Sun, Hongfu and Roosta, Fred},
 booktitle={Advances in Neural Information Processing Systems},
 year={2025}, abbr={NeurIPS}, selected={true}, bibtex_show={true},
 html={https://proceedings.neurips.cc/paper_files/paper/2025/hash/9b3edb567b651f412a175224cdb9742b-Abstract-Conference.html},
 arxiv={2511.06138}, code={https://github.com/hosseinaskari-cs/LFlow}, preview={lflow.svg}, topics={generative inverse}
}
@inproceedings{askari2025bgdm,
 title={Training-Free Medical Image Inverses via Bi-Level Guided Diffusion Models},
 author={Askari, Hossein and Roosta, Fred and Sun, Hongfu},
 booktitle={IEEE/CVF Winter Conference on Applications of Computer Vision},
 pages={75--84}, year={2025}, abbr={WACV}, selected={true}, bibtex_show={true},
 html={https://openaccess.thecvf.com/content/WACV2025/html/Askari_Training-Free_Medical_Image_Inverses_via_Bi-Level_Guided_Diffusion_Models_WACV_2025_paper.html},
 pdf={https://openaccess.thecvf.com/content/WACV2025/papers/Askari_Training-Free_Medical_Image_Inverses_via_Bi-Level_Guided_Diffusion_Models_WACV_2025_paper.pdf},
 code={https://github.com/hosseinaskari-cs/BGDM}, preview={bgdm.svg}, topics={generative inverse medical}
}
@article{askari2023mapflow,
 title={MapFlow: Latent Transition via Normalizing Flow for Unsupervised Domain Adaptation},
 author={Askari, Hossein and Latif, Yasir and Sun, Hongfu},
 journal={Machine Learning}, volume={112}, pages={2953--2974}, year={2023},
 abbr={ML}, selected={true}, bibtex_show={true}, html={https://doi.org/10.1007/s10994-023-06357-2},
 preview={mapflow.svg}, topics={adaptation}
}''')
    put('_data/publication_themes.yml','''- slug: generative
  filter_label: Generative models
  label: Generative models
  icon: '◉'
  accent: '#a18cd1'
- slug: inverse
  filter_label: Inverse problems
  label: Inverse problems
  icon: '◇'
  accent: '#397ba4'
- slug: medical
  filter_label: Medical imaging
  label: Medical imaging
  icon: '+'
  accent: '#388b75'
- slug: adaptation
  filter_label: Domain adaptation
  label: Domain adaptation
  icon: '↔'
  accent: '#b76e79' ''')
    put('_data/venues.yml','''NeurIPS:
  url: https://neurips.cc/
WACV:
  url: https://wacv.thecvf.com/
ML:
  url: https://link.springer.com/journal/10994''')
    put('_data/coauthors.yml','{}')
    for date, name, content in [('2025-11-08','lflow','LFlow is published at NeurIPS 2025.'),('2025-02-01','bgdm','BGDM appears at WACV 2025.'),('2023-07-12','mapflow','MapFlow is published in *Machine Learning*.')]:
        put(f'_news/{name}.md',f'---\nlayout: post\ndate: {date}\ninline: true\n---\n{content}')
    put('assets/img/profile.svg','''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320"><rect width="320" height="320" fill="#eee8f5"/><rect x="12" y="12" width="296" height="296" rx="5" fill="#e3d8ee"/><text x="160" y="187" text-anchor="middle" font-family="sans-serif" font-size="85" font-weight="500" fill="#76538f">HA</text></svg>''')
    for key,name,sub,color in [('lflow','LFlow','Latent flow matching','#785aa6'),('bgdm','BGDM','Bi-level diffusion guidance','#376c99'),('mapflow','MapFlow','Domain adaptation','#337a73')]:
        put('assets/img/publication_preview/'+key+'.svg',f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 160"><rect width="300" height="160" rx="5" fill="#f5f3f8"/><path d="M20 110 C75 12 120 140 180 60 S250 25 280 46" fill="none" stroke="{color}" stroke-width="3" opacity=".5"/><rect x="16" y="14" width="268" height="64" rx="5" fill="#fff" opacity=".92"/><text x="150" y="41" font-family="sans-serif" font-size="23" font-weight="bold" text-anchor="middle" fill="{color}">{name}</text><text x="150" y="62" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#555">{sub}</text><text x="150" y="148" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#777">Illustrative thumbnail</text></svg>''')
    # Only explicitly supplied assets are imported; no photo or CV from the old repo.
    for filename in ('profile.png', 'profile.jpg', 'profile.jpeg'):
        photo = ROOT / 'academic-assets' / filename
        if photo.is_file():
            shutil.copy2(photo, OUT / 'assets/img' / filename)
            p = OUT / '_pages/about.md'
            p.write_text(p.read_text().replace('image: profile.svg', 'image: ' + filename))
            break
    if (ROOT/'academic-assets/cv.pdf').is_file():
        dest=OUT/'assets/pdf/cv.pdf'; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/'academic-assets/cv.pdf',dest)
    # Publication figures: case-insensitive names, PNG preferred over PDF.
    # Convert the first page of a PDF to a browser-compatible PNG during the build.
    assets = ROOT / 'academic-assets'
    files = sorted((p for p in assets.iterdir() if p.is_file()), key=lambda p: p.name) if assets.is_dir() else []
    by_name = {p.name.casefold(): p for p in files}
    for key in ('lflow', 'bgdm', 'mapflow'):
        p = by_name.get(key + '.png') or by_name.get(key + '.pdf')
        if p is None:
            continue  # retain existing illustrative thumbnail
        dest = OUT / 'assets/img/publication_preview' / (key + '.png')
        if p.suffix.lower() == '.png':
            shutil.copy2(p, dest)
        else:
            pdf_figure_to_png(p, dest)
        bib = OUT / '_bibliography/papers.bib'
        bib.write_text(bib.read_text(encoding='utf-8').replace(f'preview={{{key}.svg}}', f'preview={{{key}.png}}'), encoding='utf-8')
        print(f'Publication figure: {p.name} -> {dest.name}')
    put('UPSTREAM.txt','Theme source: https://github.com/Luoyadan/luoyadan.github.io (source branch). Original al-folio: https://github.com/alshedivat/al-folio. MIT license; see LICENSE.')
    # Check for legacy identifiers in the retained executable layouts/includes/scripts.
    for folder in ('_includes','_layouts','_plugins','assets/js'):
        for p in (OUT/folder).rglob('*'):
            if not p.is_file() or p.suffix not in ('.html','.js','.rb','.md'): continue
            t=p.read_text(errors='ignore')
            if any(s.lower() in t.lower() for s in ['G-YB1TEJT0Y8','Yadan_latest_Resume','yadan_profile_new','3IfL11AAAAAJ','luoyadan.github.io','yadan-luo-755751132','罗雅丹']):
                # Non-used templates can be kept safely out of the site, but stop on any identity leak.
                raise RuntimeError(f'Legacy personal identifier remains in {p.relative_to(OUT)}; inspect before publishing.')
    print('Clean theme source ready:',OUT)

if __name__=='__main__':
    with tempfile.TemporaryDirectory() as tmp:
        src=Path(tmp)/'upstream'
        subprocess.run(['git','clone','--depth','1','--filter=blob:none','--sparse','--branch','source',UPSTREAM,str(src)],check=True)
        subprocess.run(['git','-C',str(src),'sparse-checkout','set','_includes','_layouts','_sass','_plugins','_pages','assets/css','assets/js','assets/fonts','assets/webfonts','assets/libs'],check=True)
        prepare(src)
