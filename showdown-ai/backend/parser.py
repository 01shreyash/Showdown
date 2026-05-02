def parse_showdown_export(paste_text: str) -> list:
    """Converts a standard Showdown text export into a list of dictionaries."""
    team = []
    # Split by double newline to separate each Pokemon
    blocks = paste_text.strip().split('\n\n')
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = block.split('\n')
        pokemon_data = {
            "species": "", "item": "", "ability": "", 
            "evs": {}, "nature": "", "moves": []
        }
        
        # Line 1: Species @ Item (or just Species)
        first_line = lines[0].split(' @ ')
        pokemon_data["species"] = first_line[0].strip().replace(' (M)', '').replace(' (F)', '') # Clean genders
        if len(first_line) > 1:
            pokemon_data["item"] = first_line[1].strip()
            
        # Parse remaining attributes
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('Ability:'):
                pokemon_data["ability"] = line.replace('Ability: ', '')
            elif line.startswith('EVs:'):
                ev_parts = line.replace('EVs: ', '').split(' / ')
                for ev in ev_parts:
                    val, stat = ev.strip().split(' ')
                    pokemon_data["evs"][stat.lower()] = int(val)
            elif line.endswith(' Nature'):
                pokemon_data["nature"] = line.replace(' Nature', '')
            elif line.startswith('- '):
                pokemon_data["moves"].append(line.replace('- ', ''))
                
        team.append(pokemon_data)
        
    return team