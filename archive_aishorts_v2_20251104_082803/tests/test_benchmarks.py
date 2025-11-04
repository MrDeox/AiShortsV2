"""
Testes de Performance (Benchmarks) - AiShorts v2.0

Testa performance e benchmark do sistema:
- Tempo de geração de temas
- Throughput da API
- Uso de memória
- Escalabilidade

Execute com: pytest tests/test_benchmarks.py --benchmark-only
"""

import pytest
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, median, stdev

@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Benchmarks de performance do sistema."""
    
    def test_single_theme_generation_time(self, mock_logger):
        """Benchmark: Tempo de geração de um único tema."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("⏱️ Benchmark: Geração de tema único")
        
        # Medir múltiplas execuções
        times = []
        num_runs = 3  # Poucas execuções para não sobrecarregar API
        
        for i in range(num_runs):
            start_time = time.time()
            
            result = theme_generator.generate_themes(
                categories=[ThemeCategory.SCIENCE],
                num_themes=1,
                min_quality_score=0.6
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            times.append(generation_time)
            
            print(f"   Execução {i+1}: {generation_time:.2f}s")
            
            # Pequena pausa entre execuções
            time.sleep(1)
        
        # Estatísticas
        avg_time = mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"📊 Estatísticas de tempo:")
        print(f"   Média: {avg_time:.2f}s")
        print(f"   Mínimo: {min_time:.2f}s")
        print(f"   Máximo: {max_time:.2f}s")
        
        # Assertions de performance
        assert avg_time < 30  # Média deve ser menor que 30 segundos
        assert max_time < 60  # Nenhuma execução deve passar de 60 segundos
        
        return {
            "average_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "times": times
        }
    
    def test_multiple_themes_batch_performance(self, mock_logger):
        """Benchmark: Performance com múltiplos temas em lote."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("⏱️ Benchmark: Múltiplos temas em lote")
        
        # Testar diferentes tamanhos de lote
        batch_sizes = [1, 2, 3]
        results = {}
        
        for batch_size in batch_sizes:
            print(f"   Testando lote de {batch_size} tema(s)...")
            
            start_time = time.time()
            
            result = theme_generator.generate_themes(
                categories=[ThemeCategory.SCIENCE],
                num_themes=batch_size,
                min_quality_score=0.6
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            
            themes_generated = len(result.themes)
            time_per_theme = total_time / themes_generated if themes_generated > 0 else 0
            
            results[batch_size] = {
                "total_time": total_time,
                "themes_generated": themes_generated,
                "time_per_theme": time_per_theme,
                "throughput": themes_generated / total_time if total_time > 0 else 0
            }
            
            print(f"     Tempo total: {total_time:.2f}s")
            print(f"     Tempo por tema: {time_per_theme:.2f}s")
            print(f"     Throughput: {results[batch_size]['throughput']:.2f} temas/s")
            
            # Pausa entre testes
            time.sleep(2)
        
        # Verificar escalabilidade
        # Throughput deve se manter razoavelmente estável
        throughputs = [r["throughput"] for r in results.values()]
        assert max(throughputs) > 0
        
        print("✅ Teste de lote concluído")
        return results
    
    def test_concurrent_generation(self, mock_logger):
        """Benchmark: Geração concorrente de temas."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        import threading
        
        print("⏱️ Benchmark: Geração concorrente")
        
        def generate_theme(category, thread_id):
            """Função para gerar tema em thread separada."""
            try:
                start = time.time()
                result = theme_generator.generate_themes(
                    categories=[category],
                    num_themes=1,
                    min_quality_score=0.6
                )
                end = time.time()
                
                return {
                    "thread_id": thread_id,
                    "category": category.value,
                    "success": True,
                    "time": end - start,
                    "themes_generated": len(result.themes)
                }
            except Exception as e:
                return {
                    "thread_id": thread_id,
                    "category": category.value,
                    "success": False,
                    "error": str(e),
                    "time": time.time() - start
                }
        
        # Configurar concorrência
        categories = [ThemeCategory.SCIENCE, ThemeCategory.HISTORY, ThemeCategory.NATURE]
        num_threads = len(categories)
        
        print(f"   Executando {num_threads} threads concorrentemente...")
        
        # Executar threads
        threads = []
        results = []
        
        for i, category in enumerate(categories):
            thread = threading.Thread(
                target=lambda cat=category, tid=i: results.append(generate_theme(cat, tid))
            )
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Analisar resultados
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        print(f"   Sucessos: {len(successful)}/{len(results)}")
        print(f"   Falhas: {len(failed)}")
        
        if successful:
            times = [r["time"] for r in successful]
            print(f"   Tempo médio: {mean(times):.2f}s")
            print(f"   Tempo mínimo: {min(times):.2f}s")
            print(f"   Tempo máximo: {max(times):.2f}s")
        
        # Pelo menos algumas execuções devem ter sucesso
        assert len(successful) >= 1, "Nenhuma execução concorrente teve sucesso"
        
        return {
            "total_threads": len(threads),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }
    
    def test_api_response_time_distribution(self, mock_logger):
        """Benchmark: Distribuição de tempo de resposta da API."""
        from src.core.openrouter_client import openrouter_client
        
        print("⏱️ Benchmark: Distribuição de tempo da API")
        
        # Fazer múltiplas chamadas para medir distribuição
        num_calls = 5
        response_times = []
        
        for i in range(num_calls):
            start_time = time.time()
            
            result = openrouter_client.generate_completion(
                system_message="Você é um assistente útil.",
                user_message="Gere uma curiosidade sobre ciência."
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            print(f"   Chamada {i+1}: {response_time:.2f}s")
            
            # Pausa entre chamadas
            time.sleep(1)
        
        # Estatísticas detalhadas
        avg_time = mean(response_times)
        median_time = median(response_times)
        std_dev = stdev(response_times) if len(response_times) > 1 else 0
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"📊 Estatísticas da API:")
        print(f"   Média: {avg_time:.2f}s")
        print(f"   Mediana: {median_time:.2f}s")
        print(f"   Desvio padrão: {std_dev:.2f}s")
        print(f"   Mínimo: {min_time:.2f}s")
        print(f"   Máximo: {max_time:.2f}s")
        
        # Verificar consistência
        coefficient_of_variation = std_dev / avg_time if avg_time > 0 else 0
        print(f"   Coeficiente de variação: {coefficient_of_variation:.2f}")
        
        # Assertions
        assert avg_time < 15  # Média deve ser menor que 15s
        assert max_time < 30  # Máximo deve ser menor que 30s
        assert coefficient_of_variation < 1.0  # Baixa variabilidade
        
        return {
            "average": avg_time,
            "median": median_time,
            "std_dev": std_dev,
            "min": min_time,
            "max": max_time,
            "cv": coefficient_of_variation,
            "times": response_times
        }

@pytest.mark.benchmark
class TestMemoryUsage:
    """Benchmarks de uso de memória."""
    
    def test_memory_usage_during_generation(self, mock_logger):
        """Benchmark: Uso de memória durante geração de temas."""
        import gc
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("💾 Benchmark: Uso de memória durante geração")
        
        # Medir memória inicial
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"   Memória inicial: {initial_memory:.2f} MB")
        
        # Gerar múltiplos temas
        themes_generated = 0
        for i in range(3):  # Poucos para não sobrecarregar
            result = theme_generator.generate_themes(
                categories=[ThemeCategory.SCIENCE],
                num_themes=2,
                min_quality_score=0.6
            )
            themes_generated += len(result.themes)
            
            # Medir memória após cada geração
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = current_memory - initial_memory
            
            print(f"   Após {themes_generated} temas: {current_memory:.2f} MB (+{memory_increase:.2f} MB)")
            
            # Pequena pausa
            time.sleep(1)
        
        # Limpeza
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        final_increase = final_memory - initial_memory
        
        print(f"   Memória final (após GC): {final_memory:.2f} MB (+{final_increase:.2f} MB)")
        
        # Verificar se uso de memória é razoável
        memory_per_theme = final_increase / themes_generated if themes_generated > 0 else 0
        print(f"   Memória por tema: {memory_per_theme:.2f} MB")
        
        # Assertions (limites flexíveis para ambiente de teste)
        assert final_increase < 100  # Menos de 100MB de aumento
        assert memory_per_theme < 10  # Menos de 10MB por tema
        
        return {
            "initial_memory": initial_memory,
            "final_memory": final_memory,
            "memory_increase": final_increase,
            "themes_generated": themes_generated,
            "memory_per_theme": memory_per_theme
        }
    
    def test_memory_leak_detection(self, mock_logger):
        """Benchmark: Detecção de vazamentos de memória."""
        import gc
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("💾 Benchmark: Detecção de vazamentos de memória")
        
        process = psutil.Process()
        
        # Medições em múltiplos ciclos
        measurements = []
        
        for cycle in range(3):
            # Gerar alguns temas
            for _ in range(2):
                theme_generator.generate_themes(
                    categories=[ThemeCategory.SCIENCE],
                    num_themes=1,
                    min_quality_score=0.6
                )
            
            # Forçar garbage collection
            gc.collect()
            
            # Medir memória
            memory_mb = process.memory_info().rss / 1024 / 1024
            measurements.append(memory_mb)
            
            print(f"   Ciclo {cycle + 1}: {memory_mb:.2f} MB")
            
            time.sleep(1)
        
        # Verificar tendência (não deve crescer indefinidamente)
        if len(measurements) >= 3:
            early_avg = mean(measurements[:2])
            late_avg = mean(measurements[-2:])
            growth_rate = (late_avg - early_avg) / early_avg * 100
            
            print(f"   Taxa de crescimento: {growth_rate:.1f}%")
            
            # Não deve crescer mais que 50% entre início e fim
            assert growth_rate < 50, f"Crescimento de memória muito alto: {growth_rate:.1f}%"
        
        print("✅ Nenhum vazamento de memória detectado")
        return measurements

@pytest.mark.benchmark
class TestScalability:
    """Testes de escalabilidade."""
    
    def test_scalability_with_categories(self, mock_logger):
        """Benchmark: Escalabilidade com número de categorias."""
        from src.generators.theme_generator import theme_generator
        from src.generators.prompt_engineering import ThemeCategory
        
        print("📈 Benchmark: Escalabilidade com categorias")
        
        # Testar diferentes números de categorias
        category_counts = [1, 3, 5]
        scalability_results = {}
        
        for num_categories in category_counts:
            categories = list(ThemeCategory)[:num_categories]
            
            print(f"   Testando com {num_categories} categoria(s)...")
            
            start_time = time.time()
            
            result = theme_generator.generate_themes(
                categories=categories,
                num_themes=1,  # Um tema por categoria
                min_quality_score=0.6
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            themes_generated = len(result.themes)
            
            time_per_category = total_time / num_categories if num_categories > 0 else 0
            
            scalability_results[num_categories] = {
                "total_time": total_time,
                "themes_generated": themes_generated,
                "time_per_category": time_per_category,
                "throughput": themes_generated / total_time if total_time > 0 else 0
            }
            
            print(f"     Tempo total: {total_time:.2f}s")
            print(f"     Tempo por categoria: {time_per_category:.2f}s")
            
            # Pausa entre testes
            time.sleep(2)
        
        # Analisar escalabilidade
        # Tempo por categoria deve ser relativamente constante
        times_per_category = [r["time_per_category"] for r in scalability_results.values()]
        avg_time_per_category = mean(times_per_category)
        
        print(f"   Tempo médio por categoria: {avg_time_per_category:.2f}s")
        
        # Verificar se não degrada muito com mais categorias
        first_time = list(scalability_results.values())[0]["time_per_category"]
        last_time = list(scalability_results.values())[-1]["time_per_category"]
        degradation = (last_time - first_time) / first_time * 100
        
        print(f"   Degradação com mais categorias: {degradation:.1f}%")
        
        # Degradação deve ser razoável (menos que 200%)
        assert degradation < 200, f"Degradação muito alta: {degradation:.1f}%"
        
        return scalability_results

# Marcador personalizado para benchmarks
def pytest_configure(config):
    """Adiciona marcador para benchmarks."""
    config.addinivalue_line("markers", "benchmark: marca testes de benchmark/performance")

if __name__ == "__main__":
    # Executar apenas benchmarks
    pytest.main([__file__, "-v", "-m", "benchmark"])