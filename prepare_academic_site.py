#!/usr/bin/env python3
"""Prepare a clean al-folio site from Yadan Luo's public MIT-licensed source.
Run from repository root: python3 prepare_academic_site.py
No old website files are copied into the generated site.
"""
import re, shutil, subprocess, tempfile
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

def prepare(src):
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    for rel in ['_includes','_layouts','_sass','_plugins','assets/css','assets/js','assets/fonts','assets/webfonts','assets/libs','Gemfile','Gemfile.lock','LICENSE','LICENSE.md']:
        copy(src, rel)
    for rel in ['_layouts/about.html','_layouts/default.html','_includes/social.html','assets/css/main.scss','Gemfile']:
        if not (OUT / rel).is_file(): raise RuntimeError('Upstream changed: missing '+rel)
    config = (src/'_config.yml').read_text()
    settings = {'title':'blank','first_name':'Hossein','middle_name':'','last_name':'Askari','email':'h.askari@uq.edu.au','description':'Generative models, Bayesian inference, and computational imaging.','footer_text':'Powered by Jekyll and al-folio.','keywords':'diffusion models, flow matching, inverse problems, computational imaging','icon':'HA','url':'https://hosseinaskari-cs.github.io','baseurl':'','github_username':'hosseinaskari-cs','cv_url':'','linkedin_username':'','scholar_userid':'','orcid_id':'0000-0002-0838-9183','google_analytics':'','panelbear_analytics':'','google_site_verification':'','bing_site_verification':'','blog_name':'Research Notes','blog_description':'','enable_google_analytics':'false','enable_panelbear_analytics':'false','enable_google_verification':'false','enable_bing_verification':'false','enable_darkmode':'true','navbar_fixed':'true','footer_fixed':'false','max_width':'1080px','news_limit':'6','enable_masonry':'false','enable_medium_zoom':'false','serve_og_meta':'false','serve_schema_org':'false','disqus_shortname':''}
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
    about = (OUT/'_layouts/about.html').read_text()
    about = re.sub(r'\s*<span class="desc zh-small">.*?</span>', '', about)
    put('_layouts/about.html',about)
    default = (OUT/'_layouts/default.html').read_text()
    default = re.sub(r'\s*<!-- Google tag \(gtag.js\) -->.*?</script>\s*<script>.*?</script>', '',default,flags=re.S)
    if 'G-YB1TEJT0Y8' in default: raise RuntimeError('Cannot remove upstream analytics tag')
    put('_layouts/default.html',default)
    put('_includes/social.html', '''<a href="mailto:{{ site.email }}" title="Email" aria-label="Email"><i class="fas fa-envelope elegant-icon"></i></a>
<a href="https://scholar.google.com/scholar?q=Hossein+Askari+diffusion+flow+matching" title="Search Google Scholar" aria-label="Search Google Scholar"><i class="ai ai-google-scholar elegant-icon"></i></a>
<a href="https://github.com/hosseinaskari-cs" title="GitHub" aria-label="GitHub"><i class="fab fa-github elegant-icon"></i></a>
<a href="https://orcid.org/0000-0002-0838-9183" title="ORCID" aria-label="ORCID"><i class="ai ai-orcid"></i></a>
{% assign cv = site.static_files | where: "path", "/assets/pdf/cv.pdf" | first %}{% if cv %}<a href="{{ '/assets/pdf/cv.pdf' | relative_url }}" title="CV" aria-label="CV"><i class="fas fa-file-alt elegant-icon"></i></a>{% endif %}''')
    put('_includes/footer.html', '''<footer class="{% if site.footer_fixed %}fixed-bottom{% else %}sticky-bottom{% endif %}"><div class="container mt-0">&copy; {{ site.time | date: '%Y' }} Hossein Askari. Powered by <a href="https://github.com/alshedivat/al-folio">al-folio</a>.</div></footer>''')
    put('_pages/about.md', '''---
layout: about
title: About
permalink: /
subtitle: Researcher in generative AI and computational imaging | <a href="https://www.uq.edu.au/">The University of Queensland</a>
profile:
  align: right
  image: profile.svg
  image_circular: true
  address:
news: true

I am a researcher working in **machine learning, computer vision, and medical imaging**. I received my PhD in Computer Science from The University of Queensland (UQ), Australia.

My research focuses on generalization, robust learning, and inverse problems.

<div style="clear:both; padding-top:15px;">

<h4>Research Interests</h4>

<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:12px;">

<div style="border:1px solid #ddd; border-radius:7px; padding:15px;">
  <i class="fas fa-network-wired" style="color:#ad2ba1;"></i>
  <strong>Out-of-Distribution Generalization</strong>
  <ul style="font-size:0.9em; padding-left:18px; margin:8px 0 0;">
    <li>Domain Adaptation</li>
    <li>Task Adaptation</li>
    <li>Domain Generalization</li>
    <li>Test-Time Adaptation</li>
  </ul>
</div>

<div style="border:1px solid #ddd; border-radius:7px; padding:15px;">
  <i class="fas fa-brain" style="color:#ad2ba1;"></i>
  <strong>In-Distribution Generalization</strong>
  <ul style="font-size:0.9em; padding-left:18px; margin:8px 0 0;">
    <li>Learning with Noisy Labels</li>
    <li>Robust Learning</li>
  </ul>
</div>

<div style="border:1px solid #ddd; border-radius:7px; padding:15px;">
  <i class="fas fa-eye" style="color:#ad2ba1;"></i>
  <strong>Inverse Problems</strong>
  <ul style="font-size:0.9em; padding-left:18px; margin:8px 0 0;">
    <li>Medical Image Reconstruction</li>
    <li>Image Restoration</li>
    <li>Computational Imaging</li>
  </ul>
</div>

</div>

<p style="margin-top:15px;">
My methodological interests include diffusion models,
flow matching, Bayesian inference, and optimization.
</p>

</div>
My goal is to develop mathematically grounded generative inference methods that combine pretrained priors with measurement consistency, enabling reliable image restoration and medical image reconstruction without task-specific retraining.

I am particularly interested in posterior sampling, latent generative models, uncertainty-aware inference, MRI and CT reconstruction, and robust learning under distribution shift. My work has appeared at NeurIPS, WACV, and in the journal *Machine Learning*.

I welcome research collaborations and am interested in postdoctoral and research scientist opportunities in generative AI, computer vision, and computational imaging.''')
    # Preserve Yadan's actual publication filtering page, with new topical data.
    pubs = (src/'_pages/publications.md').read_text()
    pubs = re.sub(r'(?m)^description:.*$', 'description: Selected research publications, organized by year and topic.',pubs)
    put('_pages/publications.md',pubs)
    put('_pages/research.md', '''---
layout: page
permalink: /research/
title: Research
description: Generative inference for inverse problems.
nav: true
nav_order: 2
---
## Generative models and posterior inference
Training-free conditional sampling using pretrained diffusion and flow-matching models, including posterior score approximation, measurement guidance, and latent inference.

## Computational imaging
Image restoration and reconstruction from incomplete or noisy measurements, including MRI, CT, deblurring, inpainting and super-resolution.

## Robust machine learning
Normalizing flows, domain adaptation and learning under distribution shift.

### Research projects

- **[LFlow](https://github.com/hosseinaskari-cs/LFlow)** — latent flow-matching inference for linear inverse problems (NeurIPS 2025).
- **[BGDM](https://github.com/hosseinaskari-cs/BGDM)** — bi-level diffusion guidance for MRI and CT reconstruction (WACV 2025).
- **[MapFlow](https://doi.org/10.1007/s10994-023-06357-2)** — latent transitions for unsupervised domain adaptation (*Machine Learning*, 2023).''')
    put('_pages/contact.md', '''---
layout: page
permalink: /contact/
title: Contact
nav: true
nav_order: 3
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
    put('assets/img/profile.svg','''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320"><rect width="320" height="320" fill="#eee8f5"/><circle cx="160" cy="160" r="148" fill="#e3d8ee"/><text x="160" y="187" text-anchor="middle" font-family="sans-serif" font-size="85" font-weight="500" fill="#76538f">HA</text></svg>''')
    for key,name,sub,color in [('lflow','LFlow','Latent flow matching','#785aa6'),('bgdm','BGDM','Bi-level diffusion guidance','#376c99'),('mapflow','MapFlow','Domain adaptation','#337a73')]:
        put('assets/img/publication_preview/'+key+'.svg',f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 160"><rect width="300" height="160" rx="5" fill="#f5f3f8"/><path d="M20 110 C75 12 120 140 180 60 S250 25 280 46" fill="none" stroke="{color}" stroke-width="3" opacity=".5"/><rect x="16" y="14" width="268" height="64" rx="5" fill="#fff" opacity=".92"/><text x="150" y="41" font-family="sans-serif" font-size="23" font-weight="bold" text-anchor="middle" fill="{color}">{name}</text><text x="150" y="62" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#555">{sub}</text><text x="150" y="148" font-family="sans-serif" font-size="10" text-anchor="middle" fill="#777">Illustrative thumbnail</text></svg>''')
    # Only explicitly supplied assets are imported; no photo or CV from the old repo.
    if (ROOT/'academic-assets/profile.jpg').is_file():
        dest=OUT/'assets/img/profile.jpg'; shutil.copy2(ROOT/'academic-assets/profile.jpg',dest)
        p=OUT/'_pages/about.md'; p.write_text(p.read_text().replace('image: profile.svg','image: profile.jpg'))
    if (ROOT/'academic-assets/cv.pdf').is_file():
        dest=OUT/'assets/pdf/cv.pdf'; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/'academic-assets/cv.pdf',dest)
    for key in ('lflow','bgdm','mapflow'):
        p=ROOT/f'academic-assets/{key}.png'
        if p.is_file():
            shutil.copy2(p,OUT/f'assets/img/publication_preview/{key}.png')
            bib=OUT/'_bibliography/papers.bib'; bib.write_text(bib.read_text().replace(f'preview={{{key}.svg}}',f'preview={{{key}.png}}'))
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
