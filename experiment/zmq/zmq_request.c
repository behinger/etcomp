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

/* ZeroMQ requester wrapper for Matlab */

#include <string.h>
#include <assert.h>
#include <zmq.h>
#include <mex.h>
#include "multi_connector.h"
#include "utils.h"

static MultiConnector *connector = NULL;

static void
close_zmq (void)
{
	if (connector != NULL)
	{
		multi_connector_free (connector);
		connector = NULL;
	}
}

static void
print_error (const char *msg)
{
	/* Clean-up before exit, so hopefully the Matlab script can be run again
	 * without restarting Matlab.
	 */
	close_zmq ();

	mexErrMsgTxt (msg);
}

static void
init_zmq (void)
{
	close_zmq ();

	assert (connector == NULL);
	connector = multi_connector_new ();
}

static int
add_requester (const char *end_point)
{
	int requester_id;
	void *socket;
	int linger_value;
	int ok;

	requester_id = multi_connector_add_socket (connector, ZMQ_REQ, end_point);

	/* If the replier isn't connected, closing the socket should not block. */
	socket = multi_connector_get_socket (connector, requester_id);
	linger_value = 0;
	ok = zmq_setsockopt (socket, ZMQ_LINGER, &linger_value, sizeof (int));
	if (ok != 0)
	{
		print_error ("zmq_request error: impossible to set linger socket option.");
	}

	return requester_id;
}

static void
send_msg (int requester_id,
	  const char *msg)
{
	void *requester;

	if (!multi_connector_valid_socket_id (connector, requester_id))
	{
		mexPrintf ("Invalid requester ID.\n");
		return;
	}

	requester = multi_connector_get_socket (connector, requester_id);
	assert (requester != NULL);

	zmq_send (requester, msg, strlen (msg), 0);
}

void
mexFunction (int n_return_values,
	     mxArray *return_values[],
	     int n_args,
	     const mxArray *args[])
{
	char *command;
	int i;

	if (n_args < 1)
	{
		print_error ("zmq_request error: you must provide the command name and the arguments.");
	}

	command = mxArrayToString (args[0]);

	for (i = 0; command[i] != '\0'; i++)
	{
		command[i] = tolower (command[i]);
	}

	if (strcmp (command, "init") == 0)
	{
		if (n_return_values > 0)
		{
			print_error ("zmq_request error: init command: "
				     "you cannot assign a result with this call.");
		}

		if (n_args > 1)
		{
			print_error ("zmq_request error: init command: too many arguments.");
		}

		init_zmq ();
	}
	else if (strcmp (command, "add_requester") == 0)
	{
		char *end_point;
		int requester_id;
		int *ret_data;

		if (n_return_values > 1)
		{
			print_error ("zmq_request error: add_requester command: "
				     "you cannot assign the result to more than one return variable.");
		}

		if (n_args > 2)
		{
			print_error ("zmq_request error: add_requester command: too many arguments.");
		}

		end_point = mxArrayToString (args[1]);

		requester_id = add_requester (end_point);

		return_values[0] = mxCreateNumericMatrix (1, 1, mxINT32_CLASS, mxREAL);
		ret_data = (int *) mxGetData (return_values[0]);
		*ret_data = requester_id;

		mxFree (end_point);
	}
	else if (strcmp (command, "send_request") == 0)
	{
		int requester_id;
		char *msg;

		if (n_return_values > 0)
		{
			print_error ("zmq_request error: send command: "
				     "you cannot assign a result with this call.");
		}

		if (n_args > 3)
		{
			print_error ("zmq_request error: send command: too many arguments.");
		}

		requester_id = utils_get_socket_id (args[1]);
		msg = mxArrayToString (args[2]);

		send_msg (requester_id, msg);

		mxFree (msg);
	}
	else if (strcmp (command, "receive_reply") == 0)
	{
		double *arg_data;
		int requester_id;
		double timeout;
		char *msg;

		if (n_return_values > 1)
		{
			print_error ("zmq_request error: receive command: "
				     "you cannot assign the result to more than one return variable.");
		}

		if (n_args > 3)
		{
			print_error ("zmq_request error: receive command: too many arguments.");
		}

		requester_id = utils_get_socket_id (args[1]);

		/* It seems that numeric types from Matlab are encoded as
		 * doubles, even if there is no decimal separator (e.g. 3000).
		 */
		if (mxGetClassID (args[2]) != mxDOUBLE_CLASS)
		{
			print_error ("zmq_request error: receive command: "
				     "the timeout has an invalid type, it should be a double.");
		}

		arg_data = (double *) mxGetData (args[2]);
		timeout = *arg_data;

		msg = multi_connector_receive_next_message (connector, requester_id, timeout);

		if (msg != NULL)
		{
			return_values[0] = mxCreateString (msg);
		}
		else
		{
			return_values[0] = mxCreateDoubleScalar (mxGetNaN ());
		}

		free (msg);
	}
	else if (strcmp (command, "close") == 0)
	{
		if (n_return_values > 0)
		{
			print_error ("zmq_request error: close command: "
				     "you cannot assign a result with this call.");
		}

		if (n_args > 1)
		{
			print_error ("zmq_request error: close command: too many arguments.");
		}

		close_zmq ();
	}
	else
	{
		print_error ("zmq_request error: unknown command.");
	}

	mxFree (command);
}
