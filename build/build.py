# -*- coding: utf-8 -*-

"""
build
~~~~~~~~~~~~~~~

Put together all files for reghdfe.ado and place them in the ../package folder

Note: Wrote in Python 2.7 but should work with Python 3.
"""

# -------------------------------------------------------------
# Imports
# -------------------------------------------------------------

from __future__ import print_function
from __future__ import division

import os, time, re, shutil, zipfile, subprocess

# -------------------------------------------------------------
# Functions
# -------------------------------------------------------------
def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))

# -------------------------------------------------------------
# Main
# -------------------------------------------------------------

# Build html help files
subprocess.call(['create_html_help.do'])

# Filenames
output_filenames = ["reghdfe.ado", "reghdfe_estat.ado", "reghdfe_p.ado", "reghdfe_footnote.ado", "hdfe.ado"]

os.chdir(os.path.split(__file__)[0])
fn_mata = ur"_mata/reghdfe.mata"
server_path = u"../package"
source_path = u"../source"

for fn in output_filenames:
    print("parsing file <{}>".format(fn))
    full_fn = os.path.join(source_path, fn)
    data = open(full_fn, "rb").read()
    source_data = None

    # Change header
    if (fn in ["reghdfe.ado", "hdfe.ado"]):
        base = fn[:-4]
        regex_string = ur'^\*! {} (\d+)\.(\d+)\.(\d+) \d+\w+\d+'.format(base)
        regex = re.search(regex_string, data)
        version = '{}.{}.{}'.format(regex.group(1), regex.group(2), int(regex.group(3))+1)
        today = time.strftime("%d%b%Y").lower() # See http://strftime.net/
        header = '*! {} {} {}'.format(base, version, today)
        data = data.replace(regex.group(0), header)
        source_data = data

    # Add Mata
    if ("include _mata/reghdfe.mata" in data):
        mata_data = open(os.path.join(source_path, fn_mata), "rb").read()
        data = data.replace(u"\r\nclear mata", mata_data)
        data = data.replace(u"\r\ninclude _mata/reghdfe.mata", mata_data)

    # Add other includes
    includes = re.findall('^\s*include "([^"]+)"', data, re.MULTILINE)
    for include in includes:
        print("    parsing include <{}>".format(include))
        full_include = os.path.join(source_path, include)
        include_data = open(full_include, "rb").read()
        data = data.replace(u'include "{}"'.format(include), '\r\n' + include_data)

    # Remove cap drop
    capdrops = re.findall('\s^\s*cap[a-z]* pr[a-z]* drop [a-zA-Z0-9_]+\s*$', data, re.MULTILINE)
    for capdrop in capdrops:
        data = data.replace(capdrop, "\n")        

    # Save
    new_fn = os.path.join(server_path, fn)
    with open(new_fn, 'wb') as new_fh:
        new_fh.write(data)

    # Override source file with correct build number
    if (fn in ["reghdfe.ado", "hdfe.ado"]):
        with open(full_fn, 'wb') as fh:
            fh.write(source_data)

# Update hdfe/reghdfe.pkg
for pkgname in ["reghdfe.pkg", "hdfe.pkg"]:
    print("updating date in " + pkgname)
    full_pkg = os.path.join(source_path, pkgname)
    pkg = open(full_pkg, "rb").read()
    today = time.strftime("%Y%m%d")
    pkg = re.sub(ur'Distribution-Date: \d+', ur'Distribution-Date: ' + today, pkg)
    open(full_pkg, 'wb').write(pkg)
    shutil.copy(full_pkg, os.path.join(server_path, pkgname))

# Copy
print("Copying misc files...")
shutil.copy(os.path.join(source_path, u"reghdfe.sthlp"), os.path.join(server_path, u"reghdfe.sthlp"))
shutil.copy(os.path.join(source_path, u"hdfe.sthlp"), os.path.join(server_path, u"hdfe.sthlp"))
shutil.copy(os.path.join(source_path, u"stata.toc"), os.path.join(server_path, u"stata.toc"))

print("Building zip file")
zipf = zipfile.ZipFile('../misc/reghdfe.zip', 'w')
zipdir('../package/', zipf)
zipf.close()

print("Done!")
