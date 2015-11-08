#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
resourceFile=$DIR/../../Resources/CompileSlicerArgs.txt
if [ ! -e $resourceFile ]
then
  echo "Resource file ($resourceFile) not found"
  echo "Resource file contains: 1)Slicer root directory"
exit 1
fi
source $DIR/../ConfigurationVariables.script
source $DIR/../../Resources/CompileEnvironment.script
resources=(`less $resourceFile`)
rootDir=${resources[0]}
develdir=$rootDir
slicerrootcompileddir=$rootDir
extensiondir=${develdir}/ExtensionsIndex
echo "Extension Index directory: $extensiondir"
if [ -d $extensiondir ]
then
  echo "Extension index already cloned. Pulling it for updates."
  cd $extensiondir
  git pull origin master
else
  echo "Extension index directory does not exist. Cloning repository."
  cd ${develdir}
  git clone https://github.com/fbudin69500/ExtensionsIndex.git
fi
system=`uname`
if [ "$system" == "Darwin" ]
then
  extraArgs="-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.10"
fi
cd $develdir
for slicerversion in Slicer-r23774 Slicer-trunk Slicer-git
do
  extensioncmakedir=${slicerrootcompileddir}/${slicerversion}/Extensions/CMake
  slicerdir=${slicerrootcompileddir}/${slicerversion}-build/Slicer-build
  if [ -e $slicerdir ]
  then
    echo $slicerdir
    mkdir ${develdir}/ExtensionsIndex-build-${slicerversion}
    cd ${develdir}/ExtensionsIndex-build-${slicerversion}
    cmake -DSlicer_DIR:PATH=${slicerdir} -DSlicer_EXTENSION_DESCRIPTION_DIR:PATH=$extensiondir -DCMAKE_BUILD_TYPE:STRING=Release -DMIDAS_PACKAGE_URL:STRING=http://slicer.kitware.com/midas3 -DMIDAS_PACKAGE_EMAIL:STRING=fbudin@unc.edu -DMIDAS_PACKAGE_API_KEY:STRING=pz2mVg4FdSYRuDy8bXQRcksfBHLjyKOO9E1TLUmO $extraArgs ${extensioncmakedir}
  else
    echo "$slicerdir does not exist"
  fi
done

#-- Setting OSX_ARCHITECTURES to 'x86_64' as none was specified.
#-- Setting OSX_DEPLOYMENT_TARGET to '10.7' as none was specified.
#-- Setting OSX_SYSROOT to '/Developer/SDKs/MacOSX10.7.sdk' as none was specified.
