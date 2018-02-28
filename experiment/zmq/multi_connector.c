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

#include "multi_connector.h"

#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <zmq.h>
#include <mex.h>
#include "utils.h"

#define MAX_SOCKETS 128

struct _MultiConnector
{
	void *context;
	void *sockets[MAX_SOCKETS];
	int next_socket_index;
};

MultiConnector *
multi_connector_new (void)
{
	MultiConnector *connector;

	connector = (MultiConnector *) malloc (sizeof (MultiConnector));
	memset (connector, 0, sizeof (MultiConnector));

	connector->context = zmq_ctx_new ();

	return connector;
}

void
multi_connector_free (MultiConnector *connector)
{
	int i;

	if (connector == NULL)
	{
		return;
	}

	for (i = 0; i < connector->next_socket_index; i++)
	{
		assert (connector->sockets[i] != NULL);
		zmq_close (connector->sockets[i]);
	}

	for (i = connector->next_socket_index; i < MAX_SOCKETS; i++)
	{
		assert (connector->sockets[i] == NULL);
	}

	if (connector->context != NULL)
	{
		zmq_ctx_destroy (connector->context);
	}

	free (connector);
}

/* Returns the socket_id */
int
multi_connector_add_socket (MultiConnector *connector,
			    int socket_type,
			    const char *end_point)
{
	void *new_socket;
	int index;
	int ok;

	if (connector->next_socket_index >= MAX_SOCKETS)
	{
		mexErrMsgTxt ("zmq multi_connector error: number of sockets limit reached, see the MAX_SOCKETS #define.");
	}

	new_socket = zmq_socket (connector->context, socket_type);

	ok = zmq_connect (new_socket, end_point);
	if (ok != 0)
	{
		mexErrMsgTxt ("zmq multi_connector error: impossible to connect to the end point.");
	}

	assert (new_socket != NULL);

	index = connector->next_socket_index;
	connector->sockets[index] = new_socket;
	connector->next_socket_index++;

	return index;
}

/* Returns whether the socket_id is valid (a boolean). */
int
multi_connector_valid_socket_id (MultiConnector *connector,
				 int socket_id)
{
	return (0 <= socket_id && socket_id < MAX_SOCKETS &&
		socket_id < connector->next_socket_index);
}

void *
multi_connector_get_socket (MultiConnector *connector,
			    int socket_id)
{
	if (!multi_connector_valid_socket_id (connector, socket_id))
	{
		return NULL;
	}

	return connector->sockets[socket_id];
}

static void
close_msg (zmq_msg_t *msg)
{
	int ok;

	ok = zmq_msg_close (msg);
	if (ok != 0)
	{
		mexErrMsgTxt ("zmq multi_connector error: impossible to close the message struct.");
	}
}

/* Receives the next zmq message as a string, with a timeout (in
 * milliseconds).
 * Free the return value with free() when no longer needed.
 */
char *
multi_connector_receive_next_message (MultiConnector *connector,
				      int socket_id,
				      double timeout)
{
	void *socket;
	int timeout_value;
	zmq_msg_t msg;
	int n_bytes;
	char *str = NULL;
	int ok;

	if (!multi_connector_valid_socket_id (connector, socket_id))
	{
		mexPrintf ("Invalid socket ID.\n");
		return NULL;
	}

	socket = connector->sockets[socket_id];
	assert (socket != NULL);

	timeout_value = timeout;
	ok = zmq_setsockopt (socket, ZMQ_RCVTIMEO, &timeout_value, sizeof (int));
	if (ok != 0)
	{
		mexErrMsgTxt ("zmq multi_connector error: impossible to set timeout option.");
	}

	ok = zmq_msg_init (&msg);
	if (ok != 0)
	{
		mexErrMsgTxt ("zmq multi_connector error: impossible to init the message struct.");
	}

	n_bytes = zmq_msg_recv (&msg, socket, 0);
	if (n_bytes > 0)
	{
		void *raw_data;

		raw_data = zmq_msg_data (&msg);
		str = strndup ((char *) raw_data, n_bytes);
	}

	close_msg (&msg);

	return str;
}
