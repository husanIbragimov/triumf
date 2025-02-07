#!/bin/bash
find docx$1 -name "*.docx" -type f -print0 | xargs -0 -n 1000 unoconv -f pdf
find docx$1 -name "*.docx" -type f -print0 | xargs -0 -n 1000 rm --
sudo mv /var/www/triumf/docx$1 /var/www/triumf/media/pdfs/$1

