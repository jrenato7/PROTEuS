#!/bin/sh
# Verificacao se servico esta online

qtde=$(ps aux | grep "search_mutant.py" | wc -l)

if test "$qtde" = "1"
then
  python /scratch/proteus/client/search_mutant.py;
#else
#  echo "Search Mutant is online." ;
#  echo "Nothing to do.";
fi
