$(document).ready(function() {
    // Adicionar novo professor
    $('#professorForm').submit(function(e) {
    e.preventDefault();
    
    // Coletar dados do formulário
    const nome = $('#nome').val();
    const materias = $('#materias').val().split(',').map(item => item.trim());
    
    // Coletar disponibilidade - CORREÇÃO AQUI
    const disponibilidade = {};
    const dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'];
    const periodos = ['manha', 'tarde', 'noite'];
    
    // Inicializa a estrutura de disponibilidade
    dias.forEach(dia => {
        disponibilidade[dia] = {};
        periodos.forEach(periodo => {
            disponibilidade[dia][periodo] = false;
        });
    });
    
    // Marca os períodos disponíveis
    $('.disponibilidade:checked').each(function() {
        const dia = $(this).data('dia');
        const periodo = $(this).data('periodo');
        if (dia && periodo && disponibilidade[dia]) {
            disponibilidade[dia][periodo] = true;
        }
    });
    
    // Verificação de dados antes de enviar
    console.log('Dados a serem enviados:', {
        nome: nome,
        materias: materias,
        disponibilidade: disponibilidade
    });
    
    // Enviar para o servidor
    $.ajax({
        url: '/professor',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            nome: nome,
            materias: materias,
            disponibilidade: disponibilidade
        }),
        success: function(response) {
            console.log('Resposta do servidor:', response);
            if (response.success && response.professor) {
                addRowToTable(response.professor);
                $('#professorForm')[0].reset();
                $('.disponibilidade').prop('checked', false);
                showAlert('Professor adicionado com sucesso!', 'success');
            } else {
                showAlert(response.error || 'Erro ao salvar professor', 'danger');
            }
        },
        error: function(xhr, status, error) {
            console.error('Erro na requisição:', error);
            showAlert('Erro ao comunicar com o servidor: ' + error, 'danger');
        }
    });
});
    
    // Editar professor
    $(document).on('click', '.edit-btn', function() {
        const professorId = $(this).data('id');
        
        $.getJSON('/professor/' + professorId, function(professor) {
            if (professor) {
                // Preencher dados básicos
                $('#editarId').val(professor.id);
                $('#editarNome').val(professor.nome);
                $('#editarMaterias').val(Array.isArray(professor.materias) ? professor.materias.join(', ') : professor.materias);
                
                // ---------- [ALTERAÇÃO 2 COMEÇA AQUI] ---------- //
                // Resetar todos os checkboxes primeiro
                $('.editarDisponibilidade').prop('checked', false);
                
                // Marcar checkboxes conforme disponibilidade
                for (const dia in professor.disponibilidade) {
                    for (const periodo in professor.disponibilidade[dia]) {
                        if (professor.disponibilidade[dia][periodo]) {
                            // Remove acentos e normaliza o nome do dia (ex: "Terça" vira "Terca")
                            const diaNormalizado = dia.normalize("NFD")
                                .replace(/[\u0300-\u036f]/g, "")
                                .replace(/\s/g, "");
                            
                            // Monta o ID do checkbox (ex: "editarSegundamanha")
                            const checkboxId = `editar${diaNormalizado}${capitalizeFirstLetter(periodo)}`;
                            
                            // Marca o checkbox correspondente
                            $(`#${checkboxId}`).prop('checked', true);
                        }
                    }
                }
                // ---------- [ALTERAÇÃO 2 TERMINA AQUI] ---------- //
                
                $('#editarProfessorModal').modal('show');
            }
        }).fail(function() {
            showAlert('Erro ao carregar dados do professor.', 'danger');
        });
    });
    
    // Salvar edição
    $('#salvarEdicaoBtn').click(function() {
        const professorId = $('#editarId').val();
        const nome = $('#editarNome').val();
        const materias = $('#editarMaterias').val().split(',').map(item => item.trim());
        
        // Coletar disponibilidade
        const disponibilidade = {
            segunda: { manha: false, tarde: false, noite: false },
            terca: { manha: false, tarde: false, noite: false },
            quarta: { manha: false, tarde: false, noite: false },
            quinta: { manha: false, tarde: false, noite: false },
            sexta: { manha: false, tarde: false, noite: false }
        };
        
        $('.editarDisponibilidade:checked').each(function() {
            const dia = $(this).data('dia');
            const periodo = $(this).data('periodo');
            disponibilidade[dia][periodo] = true;
        });
        
        // Enviar para o servidor
        $.ajax({
            url: '/professor/' + professorId,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({
                nome: nome,
                materias: materias,
                disponibilidade: disponibilidade
            }),
            success: function(response) {
                if (response.success && response.professor) {
                    // Atualizar linha na tabela
                    updateRowInTable(response.professor);
                    
                    // Fechar modal
                    $('#editarProfessorModal').modal('hide');
                    
                    // Mostrar mensagem de sucesso
                    showAlert('Professor atualizado com sucesso!', 'success');
                } else {
                    showAlert('Resposta inesperada do servidor.', 'danger');
                }
            },
            error: function(xhr, status, error) {
                showAlert('Erro ao atualizar professor: ' + error, 'danger');
            }
        });
    });
    
    // Excluir professor
    $(document).on('click', '.delete-btn', function() {
        if (confirm('Tem certeza que deseja excluir este professor?')) {
            const professorId = $(this).data('id');
            
            $.ajax({
                url: '/professor/' + professorId,
                method: 'DELETE',
                success: function(response) {
                    if (response.success) {
                        // Remover linha da tabela
                        $(`tr[data-id="${professorId}"]`).remove();
                        
                        // Mostrar mensagem de sucesso
                        showAlert('Professor excluído com sucesso!', 'success');
                    } else {
                        showAlert('Erro ao excluir professor.', 'danger');
                    }
                },
                error: function(xhr, status, error) {
                    showAlert('Erro ao excluir professor: ' + error, 'danger');
                }
            });
        }
    });
    
    // Gerar horários
    $('#gerarHorariosBtn').click(function() {
        const $btn = $(this);
        $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>Gerando...');
        $btn.prop('disabled', true);
        
        $.ajax({
            url: '/gerar_horarios',
            method: 'POST',
            success: function(response) {
                $btn.html('<i class="fas fa-magic me-2"></i>Gerar Horários');
                $btn.prop('disabled', false);
                
                if (response.success) {
                    // Mostrar resultados
                    $('#resultadoHorarios').removeClass('d-none');
                    $('#statusGeracao').text(`Status: ${response.resultado.status}`);
                    
                    // Construir tabela de horários
                    let tabelaHTML = `
                        <thead>
                            <tr>
                                <th>Horário</th>
                                ${response.resultado.professores.map(p => `<th>${p}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                    `;
                    
                    // Adicionar linhas para cada horário
                    response.resultado.horarios.forEach(horario => {
                        tabelaHTML += `
                            <tr>
                                <td>${horario.dia} ${horario.periodo}</td>
                                ${horario.alocacoes.map(aloc => `
                                    <td>${aloc.materia}</td>
                                `).join('')}
                            </tr>
                        `;
                    });
                    
                    tabelaHTML += `</tbody>`;
                    $('#tabelaHorarios').html(tabelaHTML);
                    
                    showAlert('Horários gerados com sucesso!', 'success');
                } else {
                    showAlert('Erro ao gerar horários: ' + (response.error || 'Desconhecido'), 'danger');
                }
            },
            error: function(xhr, status, error) {
                $btn.html('<i class="fas fa-magic me-2"></i>Gerar Horários');
                $btn.prop('disabled', false);
                showAlert('Erro ao conectar com o servidor: ' + error, 'danger');
            }
        });
    });
    
    // Funções auxiliares
    function addRowToTable(professor) {
        console.log('Adicionando professor à tabela:', professor);
        
        const disponibilidadeText = formatDisponibilidade(professor.disponibilidade);
        const materiasText = Array.isArray(professor.materias) ? professor.materias.join(', ') : professor.materias;
        
        const row = `
            <tr data-id="${professor.id}">
                <td>${professor.nome}</td>
                <td>${materiasText}</td>
                <td>${disponibilidadeText}</td>
                <td>
                    <button class="btn btn-sm btn-warning edit-btn" data-id="${professor.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger delete-btn" data-id="${professor.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
        
        $('#tabelaProfessores tbody').append(row);
    }
    
    function updateRowInTable(professor) {
        const disponibilidadeText = formatDisponibilidade(professor.disponibilidade);
        const materiasText = Array.isArray(professor.materias) ? professor.materias.join(', ') : professor.materias;
        
        const row = $(`tr[data-id="${professor.id}"]`);
        row.find('td:eq(0)').text(professor.nome);
        row.find('td:eq(1)').text(materiasText);
        row.find('td:eq(2)').html(disponibilidadeText);
    }
    
    function formatDisponibilidade(disponibilidade) {
    if (!disponibilidade) return 'Nenhuma disponibilidade';

    // Ordem fixa dos dias da semana
    const diasOrdenados = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'];
    const periodosTraduzidos = {
        'manha': 'Manhã',
        'tarde': 'Tarde', 
        'noite': 'Noite'
    };

    let resultado = [];

    // Percorre os dias na ordem correta
    diasOrdenados.forEach(dia => {
        if (disponibilidade[dia]) {
            const periodosDisponiveis = [];
            
            // Verifica cada período
            for (const periodo in disponibilidade[dia]) {
                if (disponibilidade[dia][periodo]) {
                    periodosDisponiveis.push(periodosTraduzidos[periodo] || periodo);
                }
            }

            // Se houver períodos disponíveis, adiciona ao resultado
            if (periodosDisponiveis.length > 0) {
                resultado.push(`${dia}: ${periodosDisponiveis.join(', ')}`);
            }
        }
    });

    return resultado.length > 0 ? resultado.join('<br>') : 'Nenhuma disponibilidade';
}
    
    function showAlert(message, type) {
        const alert = $(`
            <div class="alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3" role="alert" style="z-index: 1000;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `);
        
        $('body').append(alert);
        
        setTimeout(() => {
            alert.alert('close');
        }, 5000);
    }
    
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
});
