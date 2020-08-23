import tornado.websocket


class ExampWss(tornado.websocket):

    def get(self, msg1, msg2):
        print(f"wss get receive msg1:{msg1}, msg2:{msg2}")
        self.write(f"msg:{msg1 + '#' + msg2}")

    def post(self, msg1, msg2):
        print(f"wss post receive msg1:{msg1}, msg2:{msg2}")
        self.write(f"msg:{msg1 + '@' + msg2}")

    # def

    def open(self):
        pass