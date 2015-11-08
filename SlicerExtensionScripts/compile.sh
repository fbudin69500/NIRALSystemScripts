#!/bin/bash
develdir=@CompilationDir@
slicerrootcompileddir=@SlicerRootCompiledDir@"
extensiondir=${develdir}/ExtensionsIndex
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++
cd $develdir
for slicerversion in Slicer4.3.1-r22599 Slicer4.4.0-r23774 Slicer4-trunk
do
  slicerdir=${slicerrootcompileddir}/${slicerversion}-build/Slicer-build
  cd ${develdir}/ExtensionsIndex-build-${slicerversion}
  make DTIProcess -j2
  make DTIPrep -j2
  make FiberViewerLight -j2
  make DTIAtlasBuilder -j2
  make DTIAtlasFiberAnalyzer -j2
done

#-- Setting OSX_ARCHITECTURES to 'x86_64' as none was specified.
#-- Setting OSX_DEPLOYMENT_TARGET to '10.7' as none was specified.
#-- Setting OSX_SYSROOT to '/Developer/SDKs/MacOSX10.7.sdk' as none was specified.
