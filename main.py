import tarfile
import os
from string import Template
import argparse
import tempfile
import shutil
import subprocess


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-code", required=True, help="app code")
    parser.add_argument("--app-name", required=True, help="app name")
    parser.add_argument("--saas-path", required=True, help="saas-path")
    parser.add_argument("--dest-path", required=True, help="dest path")
    parser.add_argument("--requirements-path",
                        required=True, help="requirements-path")
    parser.add_argument("--app-desc-path", required=True, help="app-desc-path")
    parser.add_argument("--author", default='WeOps', help="author")
    parser.add_argument("--category", default='运维工具', help="category")
    parser.add_argument("--introduction", default='运维工具', help="introduction")
    parser.add_argument("--version", default='1.0.0', help="version")
    parser.add_argument("--memory", default=512, help="version")
    parser.add_argument("--use-celery", default=True, help="use-celery")

    args = parser.parse_args()

    template = Template("""app_code: $app_code    
app_name: $app_name
author: $author
category: $category
!!python/unicode 'date': '2022-12-02 16:59:34'
desktop:
  height: 720
  is_max: true
  width: 1280
introduction: $introduction
!!python/unicode 'language': python
language_support: 中文
version: version
container:
    memory: $memory""")

    data = {
        'app_code': args.app_code,
        'app_name': args.app_name,
        'author': args.author,
        'category': args.category,
        'introduction': args.introduction,
        'version': args.version,
        'memory': args.memory
    }
    result = template.substitute(data)

    result += '\n'
    if args.use_celery:
        result += 'is_use_celery: True'
    else:
        result += 'is_use_celery: False'

    result += '\nlibraries:'
    with open(args.requirements_path) as f:
        requirements = [line.strip().split("==")
                        for line in f if not line.startswith("#")]
        for obj in requirements:
            result += '\n  -name: '+obj[0]
            result += '\n   version: '+obj[1]

    with open(args.app_desc_path, 'w', encoding='utf-8') as f:
        f.writelines(result)

    temp_dir = tempfile.gettempdir()
    temp_folder = os.path.join(temp_dir, args.app_name+'_'+args.version)
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.mkdir(temp_folder)

    pkg_path = os.path.join(temp_folder, 'pkgs')
    os.mkdir(pkg_path)

    p = subprocess.Popen("pip download -i https://mirrors.cloud.tencent.com/pypi/simple -r " +
                         args.requirements_path+' -d '+pkg_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        out = p.stdout.read(1).decode()
        if out == '' and p.poll() is not None:
            break
        if out != '':
            print(out, end='')

    with open(os.path.join(temp_folder, 'install.txt'), "w") as f:
        pass

    src_path = os.path.join(temp_folder, 'src')
    shutil.copytree(args.saas_path, src_path)
    with tarfile.open(os.path.join(args.dest_path, args.app_name+'_'+args.version+'.tar.gz'), "w:gz") as tar:
        tar.add(temp_folder, arcname=os.path.basename(temp_folder))
