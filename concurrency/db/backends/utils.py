def get_trigger_name(field, opts):
    """

    :param field: Field instance
    :param opts: Options (Model._meta)
    :return:
    """
    return 'concurrency_{1.db_table}'.format(field, opts)
