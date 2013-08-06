"""
The module wraps C++/Python interface for Kaldi decoders.
"""
# Copyright (c) 2013, Ondrej Platek, Ufal MFF UK <oplatek@ufal.mff.cuni.cz>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License. #

try:
    from cffi import FFI, VerificationError
except ImportError as e:
    print '''

For running pykaldi you need cffi module installed!

'''
    raise e


def init_dec():
    ffidec = FFI()
    ffidec.cdef('''
    void pykaldi_version(int *out_major, int *out_minor, int *path);
    char* pykaldi_git_revision();

    typedef ... CKaldiDecoderWrapper;

    CKaldiDecoderWrapper* new_KaldiDecoderWrapper();
    void del_KaldiDecoderWrapper(CKaldiDecoderWrapper *d);

    size_t Decode(CKaldiDecoderWrapper *d);
    size_t HypSize(CKaldiDecoderWrapper *d);
    size_t FinishDecoding(CKaldiDecoderWrapper *d, bool);
    bool Finished(CKaldiDecoderWrapper *d);
    void FrameIn(CKaldiDecoderWrapper *d, unsigned char *frame, size_t frame_len);
    void PopHyp(CKaldiDecoderWrapper *d, int * word_ids, size_t size);
    size_t PrepareHypothesis(CKaldiDecoderWrapper *d, int * is_full);
    void Reset(CKaldiDecoderWrapper *d);
    int Setup(CKaldiDecoderWrapper *d, int argc, char **argv);

    ''')

    try:
        # TODO check how it works
        dirs = ['../../dec-wrap']
        libs = ['pykaldi']
        libdec = ffidec.verify(
            '''
            #include "dec-wrap/pykaldi-gmm-decode-faster.h"
            #include "dec-wrap/pykaldibin-utils.h"   // version
            ''',
            libraries=['c'] + libs,
            include_dirs=dirs,
            library_dirs=dirs,
            ext_package='pykaldi',
        )
    except VerificationError as e:
        print 'Have you compiled libraries: %s?' % str(libs)
        raise e
    return (ffidec, libdec)


def _version(vlib, vffi):
    major, minor, patch = vffi.new('int*'), vffi.new('int*'), vffi.new('int*')
    vlib.pykaldi_version(major, minor, patch)
    return (int(major[0]), int(minor[0]), int(patch[0]))


def _git_revision(glib, gffi):
    # git SHA has 40 characters
    git_ver = gffi.new("char*")
    git_ver = glib.pykaldi_git_revision()
    return gffi.string(git_ver)


ffidec, libdec = init_dec()
__version__ = _version(libdec, ffidec)
__git_revision__ = _git_revision(libdec, ffidec)