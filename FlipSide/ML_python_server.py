import cgi
from http.server import BaseHTTPRequestHandler, HTTPServer
import io

import sys
import graph_data_construction
import json

#insert list of question ids here
QUESTIONS = ['q{}'.format(i) for i in range(1,9)]

class PostHandler(BaseHTTPRequestHandler):

	model = graph_data_construction.Spectrum(QUESTIONS)

	def processed(self, data):
		#user_id, question_id, vote = PARSE DATA BASED ON FORM
		votes = json.loads(data)
		model.add_votes(votes)
		out = model.get_graph_data()
		# Parse output into JSON of right form
		return out

	def do_POST(self):
		try:
			if self.path.endswith('.json'):

				# Parse the form data posted
				form = cgi.FieldStorage(
					fp=self.rfile,
					headers=self.headers,
					environ={
					'REQUEST_METHOD': 'POST',
					'CONTENT_TYPE': self.headers['Content-Type'],
					}
				)

				# Begin the response
				self.send_response(200)
				self.send_header('Content-Type',
				         'text/plain; charset=utf-8')
				self.end_headers()


				# Echo back information about what was posted in the form
				for field in form.keys():
					field_item = form[field]
					if field_item.filename:
						# The field contains an uploaded file
						file_data = field_item.file.read()
						processed = self.process(file_data)
						del file_data
						json_string = json.dumps(processed)
						print('\n\nTYPE\n{}\n\n'.format(type(self.wfile)))
						self.wfile.write(json_string)
						self.wfile.close()
					else:
						pass
						'''
		            	processed = self.process(None)
		                # Regular form value
		                json_string = json.dumps(processed)
		                self.wfile.write(json_string)
		                self.wfile.close()
						'''
		except:
			self.send_error(404, 'file not found')




if __name__ == '__main__':
	print('http server is starting...')
	server = HTTPServer(('127.0.0.1', 80), PostHandler)
	print('Running server, use <Ctrl-C> to stop')
	server.serve_forever()
