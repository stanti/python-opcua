import sys
import logging

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()

from opcua import ua, Server


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our custom stuff
    objects = server.get_objects_node()

    # populating our address space
    myobj = objects.add_object(idx, "MyObject")

    # Creating a custom event: Approach 1
    # The custom event object automatically will have members from its parent (BaseEventType)
    etype = server.create_custom_event_type(2, 'MyFirstEvent', ua.ObjectIds.BaseEventType, [('MyNumericProperty', ua.VariantType.Float), ('MyStringProperty', ua.VariantType.String)])

    myevgen = server.get_event_generator(etype, myobj)
    myevgen.event.Severity = 500

    # Creating a custom event: Approach 2
    base_etype = server.get_node(ua.ObjectIds.BaseEventType)
    custom_etype = base_etype.add_subtype(2, 'MySecondEvent')
    custom_etype.add_property(2, 'MyIntProperty', ua.Variant(None, ua.VariantType.Int32))
    custom_etype.add_property(2, 'MyBoolProperty', ua.Variant(None, ua.VariantType.Boolean))

    mysecondevgen = server.get_event_generator(custom_etype, myobj)

    # starting!
    server.start()

    try:
        # time.sleep is here just because we want to see events in UaExpert
        import time
        for i in range(1, 10):
            time.sleep(10)
            myevgen.trigger(message="This is MyFirstEvent with MyNumericProperty and MyStringProperty.")
            mysecondevgen.trigger(message="This is MySecondEvent with MyIntProperty and MyBoolProperty.")

        embed()
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()
