def check_parameters(args, expected_parameters):
    unexpected_parameters = set(args) - set(expected_parameters)
    missing_parameters = set(expected_parameters) - set(args)
    
    # Checar que no haya parametros inesperados o faltantes
    if len(unexpected_parameters) > 0 or len(missing_parameters) > 0:
        return True
    return False