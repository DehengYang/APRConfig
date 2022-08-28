cd SimFix
branch=simfix_pv
git branch -f  $branch origin/$branch 
git checkout $branch
cd -

cd TBar
branch=tbar_pv
git branch -f  $branch origin/$branch 
git checkout $branch
cd -

cd nopol
branch=nopol_pv
git branch -f  $branch origin/$branch 
git checkout $branch
cd -
