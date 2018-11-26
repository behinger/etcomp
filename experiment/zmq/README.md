# A MessagePack implementation for Matlab

The code is written in pure Matlab, and has no dependencies beyond Matlab itself. It does not work in Octave, since Octave does not support `unicode2native` or `native2unicode`.

The files in this repository are taken from [Transplant](https://github.com/bastibe/transplant).

## Basic Usage:
```matlab
data = {'life, the universe, and everything', struct('the_answer', 42)};
bytes = dumpmsgpack(data)
data = parsemsgpack(bytes)
% returns: {'life, the universe, and everything', containers.Map('the_answer', 42)}
```

## Converting Matlab to MsgPack:

| Matlab         | MsgPack                   |
| -------------- | ------------------------- |
| string         | string                    |
| scalar         | number                    |
| logical        | `true`/`false`            |
| vector         | array of numbers          |
| uint8 vector   | bin                       |
| matrix         | array of array of numbers |
| empty matrix   | nil                       |
| cell array     | array                     |
| cell matrix    | array of arrays           |
| struct         | map                       |
| containers.Map | map                       |
| struct array   | array of maps             |
| handles        | raise error               |

There is no way of encoding exts

## Converting MsgPack to Matlab

| MsgPack        | Matlab         |
| -------------- | -------------- |
| string         | string         |
| number         | scalar         |
| `true`/`false` | logical        |
| nil            | empty matrix   |
| array          | cell array     |
| map            | containers.Map |
| bin            | uint8          |
| ext            | uint8          |

Note that since `structs` don't support arbitrary field names, they can't be used for representing `maps`. We use `containers.Map` instead.

## Tests
 ```matlab
 runtests()
 ```

## License

MATLAB (R) is copyright of the Mathworks

Copyright (c) 2014 Bastian Bechtold
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the
   distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

