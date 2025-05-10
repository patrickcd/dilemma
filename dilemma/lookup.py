def nested_getattr(obj, attr) -> int | float:
    """
    Given:
      - obj: an object or mapping
      - attr: a dot-separated path, e.g. "things.that.inspire"
    Returns:
      - the value at that path, or raises an AttributeError if it doesn't exist.
    """
    segments = attr.split(".")
    for i, name in enumerate(segments):
        # If this is not the last segment, check if obj is a container
        if i < len(segments) - 1:
            # For non-final segments, check if obj can contain other objects
            if not isinstance(obj, (dict, object)) or isinstance(obj, (int, float, bool)):
                msg = f"Segment '{name}' refers to a non-container: {obj!r}"
                raise AttributeError(msg)

        try:
            obj = getattr(obj, name)
        except AttributeError:
            try:
                # Check if the object is subscriptable before attempting item access
                if not hasattr(obj, "__getitem__"):
                    raise AttributeError(
                        f"Cannot resolve segment '{name}' on {obj!r} - not subscriptable"
                    )
                obj = obj[name]
            except (KeyError, TypeError):
                raise AttributeError(
                    f"Cannot resolve segment '{name}' on {obj!r}"
                ) from None

    check_numeric(obj)
    return obj


def check_numeric(value):
    """
    Check if the value is numeric (int or float).
    """
    if not isinstance(value, (int, float, bool)):
        raise TypeError(f"Expected numeric or boolean value, got {type(value).__name__}")


def compile_getter(ref, sample_context):
    """
    Given:
      - ref:    a dot-separated path, e.g. "things.that.inspire"
      - sample_context: an object/mapping whose shape matches what you'll later pass in
    Returns:
      - a function getter(context) that does exactly the same chain
        of attribute/item lookups you just validated against sample_context.
    """
    segments = ref.split(".")
    ops = []  # each entry will be ('attr', name) or ('item', name)
    cursor = sample_context

    # Figure out, at compile time, which lookup works for each segment
    for name in segments:
        # try attribute access first
        try:
            getattr(cursor, name)
            ops.append(("attr", name))
            cursor = getattr(cursor, name)
        except AttributeError:
            # if that fails, try item lookup
            try:
                cursor[name]
                ops.append(("item", name))
                cursor = cursor[name]
            except Exception as e:
                raise ValueError(f"Cannot resolve segment {name!r} on {cursor!r}") from e

    # Build a literal expression like
    #    context.things['that'].inspire
    expr = "context"
    for kind, name in ops:
        if kind == "attr":
            expr += f".{name}"
        else:
            expr += f"[{name!r}]"

    # Wrap it in a lambda that takes a context parameter
    src = f"lambda context: {expr}"

    try:
        getter = eval(src, {})  # use empty globals
    except Exception as e:
        raise ValueError(f"Failed to compile {src!r}: {e}")

    return getter
