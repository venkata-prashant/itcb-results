#!/bin/bash

function gen_fig {
	local name=$1;

	cat > sample_latex.tex <<EOF
\begin{figure}
\centering
\includegraphics{$name}
\caption{$name}
\end{figure}
EOF
}

#ls -f | while read -r file; do mv "$file" "${file// /-}" ; done

#ls -f | while read -r file; do mv "$file" "${file//_/-}" ; done

#for fname in *; do
#  name="${fname%\.*}"
#  extension="${fname#$name}"
#  newname="${name//./}"
#  newfname="$newname""$extension"
#  if [ "$fname" != "$newfname" ]; then
#    echo mv "$fname" "$newfname"
#    mv "$fname" "$newfname"
#  fi
#done

ls -f | while read -r file; do echo "\begin{figure}
%\centering
\includegraphics[width=0.9\textwidth]{$file} 
\caption{$file} 
\end{figure}
\clearpage

" >> sample_latex.tex; done