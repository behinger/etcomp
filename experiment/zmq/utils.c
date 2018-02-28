/*
 * This file is part of cosy-zeromq-matlab.
 *
 * Copyright (C) 2016 - Université Catholique de Louvain
 *
 * cosy-zeromq-matlab is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * cosy-zeromq-matlab is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
 * for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with cosy-zeromq-matlab.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Author: Sébastien Wilmet
 */

#include "utils.h"

/* Missing function on Windows (it is available on GNU/Linux).
 * Copy/paste of a simple implementation found on the web.
 */
#ifdef _WIN32
char *
strndup (const char *s,
	 size_t n)
{
	size_t len = strnlen (s, n);
	char *new = malloc (len + 1);

	if (new == NULL)
	{
		return NULL;
	}

	new[len] = '\0';
	return memcpy (new, s, len);
}
#endif

int
utils_get_socket_id (const mxArray *arg)
{
	int *arg_data;

	if (mxGetClassID (arg) != mxINT32_CLASS)
	{
		mexErrMsgTxt ("zmq_subscriber error: the subscriber_id has an invalid type, it should be int32.");
	}

	arg_data = (int *) mxGetData (arg);
	return *arg_data;
}
