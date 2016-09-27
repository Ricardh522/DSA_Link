import dslink
import random

my_num = random.randint(0, 50)


class ExampleDSLink(dslink.DSLink):
    def start(self):
        print("Starting DSLink")
        self.responder.profile_manager.create_profile("addnum")
        self.responder.profile_manager.register_callback("addnum", self.addnum)

    def update(self):
        num = random.randint(0, 50)
        my_node = self.responder.get_super_root().get("/MyNum")
        if my_node.is_subscribed():
            my_node.set_value(random.randint(0, 50))

        # Call again 2 second later
        self.call_later(2, self.update)

    def get_default_nodes(self, super_root):
        # Create MyNum Node
        # Name the node, specify the parent
        my_num = dslink.Node("MyNum", super_root)
        my_num.set_display_name("My Number")
        my_num.set_type("int")
        my_num.set_value(0)

        add_num = dslink.Node("AddNum", my_num)
        add_num.set_display_name("Add number")
        add_num.set_profile("add_num")
        add_num.set_invokable("write")
        add_num.set_parameters([
            {
                "name": "Number",
                "type": "int"
            }
        ])

        # Add my_node to the super root
        my_num.add_child(add_num)
        super_root.add_child(my_num)

        # Return the super root
        return super_root

    def addnum(self, parameters):
        num = int(parameters.params["Number"]) # Parse number
        root_node = self.responder.get_super_root()
        for child_name in root_node.children:
            child = root_node.children[child_name]

        return [[]]


class RequesterDSLink(dslink.DSLink):
    def start(self):
        self.requester.subscribe("/MyNum", self.value_updates)
        self.requester.list("/", self.recurse)
        self.requester.list("/MyNum", self.list)
        pass

    def list(self, listresponse):
        print(listresponse.node.name)
        for child in listresponse.node.children:
            print(child)

    def recurse(self, listresponse):
        for child_name in listresponse.node.children:
            child = listresponse.node.children[child_name]
            print(child.path)
            self.requester.list(child.path, self.recurse)

    def value_updates(self, data):
        print("Value updated to %s at %s" % (data[0], data[1]))


if __name__ == '__main__':
    ExampleDSLink(dslink.Configuration("example", responder=True))
    RequesterDSLink(dslink.Configuration("RequesterDSLink", requester=True, responder=False))
