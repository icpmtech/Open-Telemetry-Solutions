using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var builder = WebApplication.CreateBuilder(args);

// Adiciona serviços MVC
builder.Services.AddControllersWithViews();

// Configuração de OpenTelemetry com OTLP exporter
builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource
        .AddService("TestOpenTelemetry") // Nome da aplicação nos traces
    )
    .WithTracing(tracerBuilder => tracerBuilder
        .AddSource("TestOpenTelemetry.Controllers")
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        //.AddRedisInstrumentation() // Opcional: instalar pacote se usares Redis
        .AddOtlpExporter(otlpOptions =>
        {
            otlpOptions.Endpoint = new Uri("http://localhost:4317"); // OpenTelemetry Collector
            otlpOptions.Protocol = OpenTelemetry.Exporter.OtlpExportProtocol.Grpc;
        })
    );

var app = builder.Build();

// Pipeline HTTP
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
