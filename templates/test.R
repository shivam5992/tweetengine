#!/usr/bin/env Rscript
library('testthat')

source('rscripts/multibeta.R')

## test suites for database.r file functions

source('~/work/betablender-cl/tests/database_loadreturn.R')
source('~/work/betablender-cl/tests/database_loadindex.R')
source('~/work/betablender-cl/tests/database_loadprism.R')
source('~/work/betablender-cl/tests/database_loadfundhist.R')
source('~/work/betablender-cl/tests/database_readtarget.R')
source('~/work/betablender-cl/tests/database_loadrets.R')

# source('tests/database_loadretsdb.R')

## test suites for utility.R file functions

source('~/work/betablender-cl/tests/utility_verifydir.R')
source('~/work/betablender-cl/tests/utility_winsor.R')
source('~/work/betablender-cl/tests/utility_listday.R')
source('~/work/betablender-cl/tests/utility_parsesplitside.R')
source('~/work/betablender-cl/tests/utility_getquantile.R')

# test suite for progress.R file functions

source('~/work/betablender-cl/tests/progress_progress.R')

# test suite for mlist.R file functions

source('~/work/betablender-cl/tests/mlist_mlist.R')

# test suite for blender.R file functions

source('~/work/betablender-cl/tests/blenders_blendStatic.R')

# test suite for blocker.R file functions

source('~/work/betablender-cl/tests/blocker_blocker.R')
